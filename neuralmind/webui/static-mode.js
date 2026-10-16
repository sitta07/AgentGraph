"use strict";
// Loaded only by the static build (tools/build_site.py), before common.js.
// Defines window.NEURALMIND_STATIC.fetch, which api() uses in place of fetch():
// Playground requests go to the Python engine running in a Web Worker
// (pyodide-worker.js); Discovery Lab requests read JSON precomputed at build
// time. Both resolve to ordinary Response objects.
(function () {
  const INSTALL = "git clone https://github.com/sitta07/NeuralMind.git && cd NeuralMind\n" +
    "pip install -r requirements-neuralmind.txt -r requirements-server.txt -r requirements-research.txt\n" +
    "python -m neuralmind.server";
  const reply = (status, data) => new Response(JSON.stringify(data),
    {status, headers: {"Content-Type": "application/json"}});

  function lab(path) {
    const name = path.slice("/api/lab/".length);
    if (name === "run")
      return reply(501, {detail: "running studies needs a local install (see Run studies yourself)"});
    if (name.startsWith("report/")) return fetch(`data/lab/reports/${name.slice("report/".length)}.json`);
    return fetch(`data/lab/${name}.json`);
  }

  // ---------- boot overlay ----------
  let overlay = null;
  function showBoot(text, failed) {
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.className = "boot";
      overlay.setAttribute("role", "status");
      overlay.setAttribute("aria-live", "polite");
      overlay.innerHTML = `<div class="boot-card"><b>Starting the simulation in your browser</b>
        <p class="boot-msg"></p>
        <p class="note boot-note">The real Python engine runs here through WebAssembly (Pyodide).
          The first visit downloads about 8 MB; later visits load from the browser cache.</p></div>`;
      document.body.appendChild(overlay);
    }
    overlay.querySelector(".boot-msg").textContent = text;
    if (failed) {
      overlay.classList.add("failed");
      overlay.querySelector("b").textContent = "The simulation could not start in this browser";
      overlay.querySelector(".boot-note").innerHTML =
        "Use a recent Chrome, Edge, Firefox or Safari with WebAssembly enabled, then reload. " +
        "Or run it on your own machine:<pre><code></code></pre>";
      overlay.querySelector("code").textContent = INSTALL;
    }
  }

  // ---------- the engine worker ----------
  let worker = null, nextId = 1, failure = null;
  const pending = new Map();
  function fail(reason) {
    failure = reason;
    showBoot(reason, true);
    for (const done of pending.values()) done(reply(503, {detail: "the in-browser engine did not start"}));
    pending.clear();
  }
  function startWorker() {
    if (typeof WebAssembly !== "object" || typeof Worker !== "function") {
      fail("This browser does not support WebAssembly or Web Workers.");
      return;
    }
    showBoot("Starting…");
    worker = new Worker("static/pyodide-worker.js");
    worker.onerror = (e) => { e.preventDefault(); fail(e.message || "The engine worker crashed."); };
    worker.onmessage = ({data}) => {
      if (data.progress) showBoot(data.progress);
      else if (data.ready) { overlay.remove(); overlay = null; }
      else if (data.fatal) fail("Loading failed: " + data.fatal);
      else { pending.get(data.id)(new Response(data.text,
        {status: data.status, headers: {"Content-Type": "application/json"}})); pending.delete(data.id); }
    };
  }
  function engine(path, opts) {
    if (!worker && !failure) startWorker();
    if (failure) return Promise.resolve(reply(503, {detail: "the in-browser engine did not start"}));
    const id = nextId++;
    return new Promise((resolve) => {
      pending.set(id, resolve);
      worker.postMessage({id, path, body: opts.body === undefined ? null : opts.body});
    });
  }

  window.NEURALMIND_STATIC = {
    install: INSTALL,
    fetch: (path, opts = {}) => path.startsWith("/api/lab/") ? lab(path) : engine(path, opts),
  };
})();
