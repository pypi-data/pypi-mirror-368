import re
import importlib.resources as pkg_resources

HEAD_RE = re.compile(r"(<\s*head\b[^>]*>)", re.IGNORECASE)
BODY_RE = re.compile(r"(<\s*body\b[^>]*>)", re.IGNORECASE)
INJECTED_SCRIPT_PATH = pkg_resources.files("browser_ui").joinpath("injected_script.js")
with open(str(INJECTED_SCRIPT_PATH), "r") as f:
    INJECTED_SCRIPT = f.read()

def inject_script(html: str) -> str:
    SCRIPT = f"<script>{INJECTED_SCRIPT}</script>"
    if HEAD_RE.search(html):
        return HEAD_RE.sub(r"\1" + SCRIPT, html, 1)
    if BODY_RE.search(html):
        return BODY_RE.sub(r"\1" + SCRIPT, html, 1)
    return SCRIPT + html
