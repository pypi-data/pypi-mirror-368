globalThis.requestBackend = async function (method, payload = null) {
  const response = await fetch(`/__method__/${method}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const isGeneratorResponse = response.headers.get("X-BrowserUI-Stream-Response") === "true";
  if (isGeneratorResponse) return streamIteratorFactory(response);

  const result = await response.json();
  return result;
};

function streamIteratorFactory(response) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  return {
    async *[Symbol.asyncIterator]() {
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const decoded = decoder.decode(value);
          yield JSON.parse(decoded);
        }
      } finally {
        reader.releaseLock();
      }
    }
  };
}

// page events listener register
window.addEventListener("pagehide", (e) => {
  if (e.persisted) return;
  eventSource.close();
  navigator.sendBeacon("/__event__/page_closed");
});
window.addEventListener("DOMContentLoaded", () => {
  fetch("/__event__/page_loaded", { method: "POST" });
});

// start SSE client
const eventSource = new EventSource("/__sse__");
eventSource.onerror = function (err) {
  console.error("EventSource failed:", err);
};
globalThis.backendListener = {
  on: (event, callback) => {
    eventSource.addEventListener(event, (e) => {
      callback(e.data);
    });
  },
  off: (event, callback) => {
    eventSource.removeEventListener(event, callback);
  },
  once: (event, callback) => {
    eventSource.addEventListener(event, callback, {
      once: true
    });
  },
};
