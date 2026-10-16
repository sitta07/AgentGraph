"use strict";
// Web Worker for the static (GitHub Pages) build: runs the real Python engine
// in Pyodide and answers Playground /api/* requests through
// neuralmind.playground.dispatch. Messages in: {id, path, body} where body is a
// JSON string, or null for a GET. Messages out: {progress}, {ready}, {fatal},
// and {id, status, text} with text the JSON response body.
const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v0.29.5/full/";

const quiet = {messageCallback: () => {}};
let dispatch = null, session = null;

async function boot() {
  postMessage({progress: "Downloading the Python runtime (Pyodide)…"});
  importScripts(PYODIDE + "pyodide.js");
  const py = await loadPyodide({indexURL: PYODIDE});
  postMessage({progress: "Loading NumPy…"});
  await py.loadPackage("numpy", quiet);
  postMessage({progress: "Loading the NeuralMind engine…"});
  const r = await fetch("neuralmind.zip");
  if (!r.ok) throw new Error(`could not download neuralmind.zip (HTTP ${r.status})`);
  py.unpackArchive(await r.arrayBuffer(), "zip", {extractDir: "/home/pyodide/nm"});
  py.runPython("import sys; sys.path.insert(0, '/home/pyodide/nm')\n" +
               "from neuralmind import playground\nSESSION = playground.Session()");
  dispatch = py.globals.get("playground").dispatch;
  session = py.globals.get("SESSION");
}

const booted = boot().then(
  () => postMessage({ready: true}),
  (e) => { postMessage({fatal: String(e && e.message || e)}); throw e; });

onmessage = async ({data: {id, path, body}}) => {
  try { await booted; }
  catch (e) {
    postMessage({id, status: 503, text: JSON.stringify({detail: "the in-browser engine did not start"})});
    return;
  }
  try {
    // JS null becomes pyodide's jsnull, not None, so a GET omits the argument.
    const out = body === null ? dispatch(session, path) : dispatch(session, path, body);
    const [status, text] = out.toJs();
    out.destroy();
    postMessage({id, status, text});
  } catch (e) {
    console.error(e);
    const last = String(e && e.message || e).trim().split("\n").pop();
    postMessage({id, status: 500, text: JSON.stringify({detail: last})});
  }
};
