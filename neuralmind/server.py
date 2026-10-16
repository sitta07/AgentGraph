"""FastAPI backend for the NeuralMind Artificial Life Playground.

The browser talks to THIS server, which runs the real NumPy neural-agent engine
(:mod:`neuralmind.world`) through :mod:`neuralmind.playground`; this module only
adds HTTP routes, the Discovery Lab router and a SQLite store for saved
episodes. Runs fully offline with no API key.

Launch:
    python -m neuralmind.server            # then open http://127.0.0.1:8000
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from neuralmind import playground
from neuralmind.lab import RESULTS as LAB_RESULTS, router as lab_router
from neuralmind.persistence.store import ExperimentStore

app = FastAPI(title="NeuralMind Artificial Life Playground")

_WEBUI = Path(__file__).parent / "webui"


class Session(playground.Session):
    """The Playground session plus a local SQLite store for saved episodes."""

    def __init__(self) -> None:
        super().__init__()
        self.store = ExperimentStore("neuralmind_playground.sqlite")


SESSION = Session()


@app.exception_handler(playground.PlaygroundError)
def _playground_error(_: Request, e: playground.PlaygroundError):
    return JSONResponse({"detail": e.detail}, status_code=e.status)


@app.post("/api/session")
def create_session(body: dict | None = None):
    return SESSION.create(body or {})


@app.post("/api/step")
def step(body: dict | None = None):
    return SESSION.step(body or {})


@app.get("/api/brain/{agent_id}")
def brain(agent_id: int):
    return SESSION.brain(agent_id)


@app.get("/api/lineage")
def lineage(limit: int = 3000):
    return SESSION.lineage(limit)


@app.post("/api/advance")
def advance(body: dict | None = None):
    return SESSION.advance(body or {})


@app.post("/api/place_food")
def place_food(body: dict | None = None):
    return SESSION.place_food(body or {})


@app.post("/api/deprive")
def deprive(body: dict | None = None):
    return SESSION.deprive(body or {})


@app.post("/api/reset")
def reset(body: dict | None = None):
    return SESSION.reset(body or {})


@app.post("/api/config")
def set_config(body: dict | None = None):
    return SESSION.set_config(body or {})


@app.post("/api/train")
def train(body: dict | None = None):
    return SESSION.train(body or {})


@app.post("/api/compare")
def compare(body: dict | None = None):
    return SESSION.compare(body or {})


@app.post("/api/save")
def save(body: dict | None = None):
    result = SESSION.episode_result((body or {}).get("note", ""))
    return {"id": SESSION.store.save(result)}


@app.get("/api/runs")
def runs():
    return {"runs": SESSION.store.list()}


@app.get("/api/health")
def health():
    return {"ok": True, "has_session": SESSION.world is not None}


@app.get("/")
def index():
    return FileResponse(_WEBUI / "index.html")


@app.get("/lab")
@app.get("/lab.html")
def lab_page():
    return FileResponse(_WEBUI / "lab.html")


app.include_router(lab_router)
if LAB_RESULTS.exists():
    app.mount("/results", StaticFiles(directory=str(LAB_RESULTS)), name="results")


if _WEBUI.exists():
    app.mount("/static", StaticFiles(directory=str(_WEBUI)), name="static")


def main(argv=None) -> None:
    import argparse

    import uvicorn
    ap = argparse.ArgumentParser(description="NeuralMind Playground + Discovery Lab server")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args(argv)
    print(f"NeuralMind Playground -> http://{a.host}:{a.port}   Discovery Lab -> http://{a.host}:{a.port}/lab")
    uvicorn.run(app, host=a.host, port=a.port, log_level="warning")


if __name__ == "__main__":
    main()
