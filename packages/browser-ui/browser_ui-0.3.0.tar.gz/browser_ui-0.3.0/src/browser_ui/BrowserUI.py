import queue
import re
import webbrowser
import requests
import json
import importlib.resources as pkg_resources
from typing import Callable, cast
from pathlib import Path
from urllib.parse import urljoin
from threading import Thread, Event
from inspect import isgeneratorfunction
from cheroot import wsgi
from bottle import Bottle, SimpleTemplate, abort, request, static_file, response, redirect

from .utils import Serializable, SerializableCallable, GeneratorCallable, EventType,\
                   get_caller_file_abs_path

HEAD_RE = re.compile(r"(<\s*head\b[^>]*>)", re.IGNORECASE)
BODY_RE = re.compile(r"(<\s*body\b[^>]*>)", re.IGNORECASE)
INJECTED_SCRIPT_PATH = pkg_resources.files("browser_ui").joinpath("injected_script.js")
with open(str(INJECTED_SCRIPT_PATH), "r") as f:
    INJECTED_SCRIPT = f.read()

def server_factory(app: Bottle, port: int, server_name: str='browser-ui-server') -> wsgi.Server:
    return wsgi.Server(
        ('localhost', port), app,
        server_name=server_name,
    )

class BrowserUI:
    def __init__(self,
        static_dir: str | None = None,
        port: int = 8080,
        dev_server_url: str | None = None,
    ):
        """_summary_

        Args:
            static_dir (str | None): _description_. The target static directory.
            port (int, optional): _description_. Defaults to 8080.
            dev_server_url (str | None, optional): _description_. Defaults to None.
                The argument specifies the dev server, which is useful when this framework works with frontend scaffolds like Vite. 
                If this argument is specified, the static_dir argument will be ignored.
        """
        if static_dir is None and dev_server_url is None:
            raise ValueError("Either static_dir or dev_server_url must be specified.")

        if dev_server_url is None:
            assert static_dir is not None
            self._static_dir = self._resolve_static_dir_path(static_dir)
            self._dev_server_url = None
            self._is_dev = False
        else:
            self._dev_server_url = dev_server_url
            self._static_dir = None
            self._is_dev = True

        self._is_used = False
        self._port = port
        self._stop_event = Event()
        self._thread = Thread(target=self._run)

        self._app = Bottle()
        self._method_map: dict[str, SerializableCallable | GeneratorCallable] = {}
        self._event_map: dict[EventType, list[SerializableCallable]] = {}
        self._format_map: dict[str, Serializable] = {}
        self._server = server_factory(self._app, port)
        self._sse_queue: queue.Queue[tuple[str, Serializable]] = queue.Queue()
        self._app.route("/", callback=self._serve_static_file)
        self._app.route("/<path:path>", callback=self._serve_static_file)
        self._app.route("/__method__/<method_name>", method="POST", callback=self._serve_method)
        self._app.route("/__event__/<event_name>", method="POST", callback=self._serve_event)
        self._app.route("/__sse__", callback=self._serve_sse)

        @self._app.hook('after_request')  
        def _set_no_cache():
            response.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')  
            response.set_header('Pragma', 'no-cache')  
            response.set_header('Expires', '0')

    @staticmethod
    def _resolve_static_dir_path(static_dir: str) -> Path:
        if Path(static_dir).is_absolute():
            return Path(static_dir)
        else:
            return Path(get_caller_file_abs_path(1)).parent.joinpath(static_dir)

    @staticmethod
    def _inject_script(html: str) -> str:
        SCRIPT = f"<script>{INJECTED_SCRIPT}</script>"
        if HEAD_RE.search(html):
            return HEAD_RE.sub(r"\1" + SCRIPT, html, 1)
        if BODY_RE.search(html):
            return BODY_RE.sub(r"\1" + SCRIPT, html, 1)
        return SCRIPT + html

    def _run(self):
        self._server.prepare()
        self._server.serve()

    def _serve_html_file(self, path: str) -> str:
        if self._is_dev:
            assert self._dev_server_url is not None
            response = requests.get(urljoin(self._dev_server_url, path))
            html_content = response.text
        else:
            assert self._static_dir is not None
            with open(str(self._static_dir.joinpath(path)), "r") as f:
                html_content = f.read()
        html_content = self._inject_script(html_content)
        template = SimpleTemplate(html_content)
        return template.render(self._format_map)

    def _serve_static_file(self, path: str="index.html"):
        if path.endswith(".html") or path.endswith(".htm"):
            return self._serve_html_file(path)
        if self._is_dev:
            assert self._dev_server_url is not None
            return redirect(urljoin(self._dev_server_url, path))
        else:
            assert self._static_dir is not None
            return static_file(path, root=self._static_dir)

    def _serve_method(self, method_name: str):
        data = request.json
        if method_name not in self._method_map:
            abort(404, f"Method {method_name} is not implemented.")

        method = self._method_map[method_name]

        if isgeneratorfunction(method):
            response.set_header("X-BrowserUI-Stream-Response", "true")
            for res in cast(GeneratorCallable, method)(data):
                yield json.dumps(res)
        else:
            res = cast(SerializableCallable, method)(data)
            return json.dumps(res)

    def _serve_event(self, event_name: str):
        event = EventType.from_str(event_name)
        if event not in self._event_map:
            abort(404, f"Event {event_name} is not implemented.")
        for callback in self._event_map[event]:
            callback()

    def _serve_sse(self):
        response.set_header("Content-Type", "text/event-stream")
        response.set_header("Cache-Control", "no-cache")
        while not self._stop_event.is_set():
            try:
                event, data = self._sse_queue.get(timeout=0.01)
                yield f"event: {event}\ndata: {json.dumps(data)}\n\n"
            except queue.Empty: continue

    def add_event_listener(self, event_type: EventType, callback: Callable):
        if event_type not in self._event_map:
            self._event_map[event_type] = []
        self._event_map[event_type].append(callback)

    def register_method(self, method_name: str, method: SerializableCallable | GeneratorCallable):
        self._method_map[method_name] = method

    def register_template_vars(self, **args: Serializable):
        for k, v in args.items():
            self._format_map[k] = v

    def send_event(self, event: str, data: Serializable):
        self._sse_queue.put((event, data))

    def start(self, path: str | None = None):
        if self._is_used:
            raise RuntimeError("This BrowserUI instance has already been used and cannot be reused.")
        self._thread.start()
        final_path = f"http://localhost:{self._port}"\
                     if path is None else\
                     urljoin(f"http://localhost:{self._port}", path)
        webbrowser.open_new_tab(final_path)

    def stop(self):
        self._stop_event.set()
        self._server.stop()
        self._thread.join()
        self._is_used = True
