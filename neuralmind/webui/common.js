"use strict";
// Shared by the Playground and the Discovery Lab: DOM helpers, the toast, and
// the one fetch wrapper every request goes through.
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"']/g, c =>
  ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));

function toast(msg, kind) {
  const t = $("toast"); if (!t) return;
  t.textContent = msg;
  t.classList.toggle("error", kind === "error");
  t.classList.add("show");
  clearTimeout(t._h);
  t._h = setTimeout(() => t.classList.remove("show"), kind === "error" ? 7000 : 2600);
}

const FIX_BY_STATUS = {
  400: "Check the values you entered and try again.",
  404: "Reload the page; if it persists, create a new world.",
  409: "Wait for the running job to finish, then try again.",
};

// In the static build (static-mode.js) requests go to NEURALMIND_STATIC.fetch
// instead of the network; the responses have the same shape either way.
// Resolves to the parsed JSON body, or null on failure. `what` names the action
// ("Training"). On failure the plain-language message is in api.lastError; it is
// also shown as a toast unless `quiet` (for callers that show it inline).
async function api(path, {body, what = "The request", quiet = false} = {}) {
  const opts = body === undefined ? {} : {method: "POST",
    headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)};
  const fail = (message) => {
    api.lastError = message;
    if (!quiet) toast(message, "error");
    return null;
  };
  const STATIC = window.NEURALMIND_STATIC;
  let r;
  try { r = await (STATIC ? STATIC.fetch(path, opts) : fetch(path, opts)); }
  catch (e) {
    return fail(STATIC ? `${what} failed: this page could not load its data. Check your connection, then reload.`
      : `${what} failed: the NeuralMind server is not reachable. ` +
        "Start it with `python -m neuralmind.server`, then reload this page.");
  }
  if (!r.ok) {
    const detail = (await r.json().catch(() => ({}))).detail || r.statusText;
    const fix = FIX_BY_STATUS[r.status] ||
      `Try again; if it keeps failing, ${STATIC ? "reload the page" : "restart the server"}.`;
    return fail(`${what} failed: ${detail}. ${fix}`);
  }
  return r.json();
}
