from __future__ import annotations
import os
from pathlib import Path
from typing import Optional, Callable, Any
import inspect
import json
import shlex

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from time import time
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import urlparse

from ..core import process
from ..tools import image as image_tools
from ..tools import llm as llm_tools
from ..tools.llm import start_fastchat_background, start_ollama_background
from ..core import models as models_core
from ..core import models_index as models_index
from ..core import models_download as models_dl
from ..core.base import run_setup_wizard
from ..core.config import get_base_dir
from ..core.utils import run_bash, has_cmd

# Minimal FastAPI app exposing core functionality with a simple UI
app = FastAPI(title="ROCm-WSL-AI Web UI", version="0.2.0")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Utilities
SUPPORTED_TOOLS = {
    "comfyui": {
        "start": image_tools.start_comfyui,
        "start_bg": image_tools.start_comfyui_background,
        "stop": lambda: process.stop("comfyui"),
        "status": lambda: process.status("comfyui"),
        "logs": lambda: process.logs_path("comfyui"),
        "install": image_tools.install_comfyui,
    "category": "image",
    "url": "http://localhost:8188",
    },
    "sillytavern": {
        "start": llm_tools.start_sillytavern,
        "start_bg": llm_tools.start_sillytavern_background,
        "stop": lambda: process.stop("sillytavern"),
        "status": lambda: process.status("sillytavern"),
        "logs": lambda: process.logs_path("sillytavern"),
        "install": llm_tools.install_sillytavern,
    "category": "chat-ui",
    "url": "http://localhost:8000",
    },
    # Install-only (start/stop/status TBD)
    "sdnext": {
        "install": image_tools.install_sdnext,
    "start_bg": image_tools.start_sdnext_background,
    "stop": lambda: process.stop("sdnext"),
    "status": lambda: process.status("sdnext"),
    "category": "image",
    "url": "http://localhost:7860",
    },
    "fooocus": {
        "install": image_tools.install_fooocus,
    "start_bg": image_tools.start_fooocus_background,
    "stop": lambda: process.stop("fooocus"),
    "status": lambda: process.status("fooocus"),
    "category": "image",
    "url": "http://localhost:7865",
    },
    "forge": {
        "install": image_tools.install_forge,
    "start_bg": image_tools.start_forge_background,
    "stop": lambda: process.stop("forge"),
    "status": lambda: process.status("forge"),
    "category": "image",
    "url": "http://localhost:7860",
    },
    "a1111": {
        "install": image_tools.install_a1111,
    "start_bg": image_tools.start_a1111_background,
    "stop": lambda: process.stop("a1111"),
    "status": lambda: process.status("a1111"),
    "category": "image",
    "url": "http://localhost:7860",
    },
    "invokeai": {
        "install": image_tools.install_invokeai,
    "start_bg": image_tools.start_invokeai_background,
    "stop": lambda: process.stop("invokeai"),
    "status": lambda: process.status("invokeai"),
    "category": "image",
    "url": "http://localhost:9090",
    },
    "textgen": {
        "install": llm_tools.install_textgen,
    "start_bg": llm_tools.start_textgen_background,
    "stop": lambda: process.stop("textgen"),
    "status": lambda: process.status("textgen"),
    "category": "llm",
    "url": "http://localhost:7860",
    },
    "llama.cpp": {
        "install": llm_tools.install_llama_cpp,
    "start_bg": llm_tools.start_llama_cpp_background,
    "stop": lambda: process.stop("llama.cpp"),
    "status": lambda: process.status("llama.cpp"),
    "category": "llm",
    "url": "http://localhost:8080",
    },
    "koboldcpp": {
        "install": llm_tools.install_koboldcpp,
    "start_bg": llm_tools.start_koboldcpp_background,
    "stop": lambda: process.stop("koboldcpp"),
    "status": lambda: process.status("koboldcpp"),
    "category": "llm",
    "url": "http://localhost:5001",
    },
    "fastchat": {
    "install": llm_tools.install_fastchat,
    "start_bg": start_fastchat_background,
    "stop": lambda: process.stop("fastchat"),
    "status": lambda: process.status("fastchat"),
    "logs": lambda: process.logs_path("fastchat"),
    "category": "llm",
    "url": "http://localhost:7861",
    },
    "ollama": {
    "install": llm_tools.install_ollama,
    "start_bg": start_ollama_background,
    "stop": lambda: process.stop("ollama"),
    "status": lambda: process.status("ollama"),
    "logs": lambda: process.logs_path("ollama"),
    "category": "llm",
    "url": "http://localhost:11434",
    },
}


# Build a snapshot of tools with status and capabilities
def tool_snapshot() -> dict[str, dict]:
    snap: dict[str, dict] = {}
    for name, ops in SUPPORTED_TOOLS.items():
        alive, pid = ops.get("status", lambda: (False, None))()
        cfg = TOOLS_SETTINGS.get(name)
        snap[name] = {
            "alive": alive,
            "pid": pid,
            "category": ops.get("category"),
            "can_start": bool(ops.get("start") or ops.get("start_bg")),
            "can_stop": bool(ops.get("stop")),
            "has_logs": True,
            "url": cfg.get("url") or ops.get("url"),
            "extra_args": cfg.get("extra_args"),
        }
    return snap

# Simple Job/Progress Manager
@dataclass
class Job:
    id: str
    name: str
    created: float = field(default_factory=time)
    status: str = "queued"  # queued|running|done|error
    progress: float = 0.0  # 0..1
    message: str = ""
    error: str | None = None


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = asyncio.Lock()
        self._executor = ThreadPoolExecutor(max_workers=4)
        # Persist to JSON in config dir
        from ..core.config import _config_path
        self._hist_path = _config_path().parent / "jobs.json"
        try:
            if self._hist_path.exists():
                import json
                data = json.loads(self._hist_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    for j in data[-200:]:
                        job = Job(**j)
                        self._jobs[job.id] = job
        except Exception:
            pass

    async def create(self, name: str) -> Job:
        jid = f"job-{int(time()*1000)}"
        job = Job(id=jid, name=name)
        async with self._lock:
            self._jobs[jid] = job
        return job

    async def list(self) -> list[Job]:
        async with self._lock:
            return list(self._jobs.values())

    async def get(self, jid: str) -> Job | None:
        async with self._lock:
            return self._jobs.get(jid)

    async def run_steps(self, job: Job, steps: list[tuple[str, Callable[[], Any]]]):
        job.status = "running"
        total = len(steps) or 1

        loop = asyncio.get_running_loop()

        for i, (label, fn) in enumerate(steps, start=1):
            job.message = label
            job.progress = (i - 1) / total + 0.01
            try:
                # Run blocking step in thread
                await loop.run_in_executor(self._executor, fn)
            except Exception as e:
                job.status = "error"
                job.error = str(e)
                job.message = f"Fehler bei: {label}"
                job.progress = (i - 1) / total
                return
            job.progress = i / total
        job.status = "done"
        job.message = "Fertig"
        # persist history (truncate)
        try:
            import json
            hist = sorted((asdict(j) for j in self._jobs.values()), key=lambda x: x["created"]) [-500:]
            self._hist_path.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass


JOBS = JobManager()


class ToolsSettings:
    def __init__(self) -> None:
        from ..core.config import _config_path
        self._path = _config_path().parent / "tools.json"
        self._data: dict[str, dict] = {}
        try:
            if self._path.exists():
                self._data = json.loads(self._path.read_text(encoding="utf-8")) or {}
        except Exception:
            self._data = {}

    def get(self, tool: str) -> dict:
        return dict(self._data.get(tool, {}))

    def all(self) -> dict[str, dict]:
        return {k: dict(v) for k, v in self._data.items()}

    def get_defaults(self) -> dict:
        return dict(self._data.get("__defaults__", {}))

    def update(self, tool: str, **kwargs) -> dict:
        entry = self._data.get(tool, {})
        for k, v in kwargs.items():
            if v is not None:
                entry[k] = v
        self._data[tool] = entry
        try:
            self._path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
        return dict(entry)


TOOLS_SETTINGS = ToolsSettings()


class WebSettings:
    """Persist lightweight Web UI settings in config dir (e.g., auth choice)."""
    def __init__(self) -> None:
        from ..core.config import _config_path
        self._path = _config_path().parent / "web.json"
        self._data: dict[str, Any] = {}
        try:
            if self._path.exists():
                self._data = json.loads(self._path.read_text(encoding="utf-8")) or {}
        except Exception:
            self._data = {}

    def save(self) -> None:
        try:
            self._path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def auth_decided(self) -> bool:
        return "auth_enabled" in self._data

    def auth_enabled(self) -> bool:
        return bool(self._data.get("auth_enabled"))

    def token(self) -> str | None:
        t = self._data.get("token")
        return str(t) if t else None

    def set_auth(self, enabled: bool, token: str | None = None) -> None:
        self._data["auth_enabled"] = bool(enabled)
        if enabled:
            self._data["token"] = token or self._data.get("token") or ""
        self.save()


WEB_SETTINGS = WebSettings()

# Optional Auth (simple token). Set env ROCMWSL_WEB_TOKEN to enable.
AUTH_TOKEN = os.environ.get("ROCMWSL_WEB_TOKEN")

def _current_token() -> str | None:
    # Env var overrides any stored config
    if AUTH_TOKEN:
        return AUTH_TOKEN
    if WEB_SETTINGS.auth_enabled():
        return WEB_SETTINGS.token()
    return None

def _is_authorized(request: Request) -> bool:
    token = _current_token()
    if not token:
        return True  # auth disabled
    # Accept cookie, header or query param
    if request.cookies.get("x-auth") == token:
        return True
    if request.headers.get("x-auth") == token:
        return True
    if request.query_params.get("token") == token:
        return True
    return False


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Bypass for static and login
    path = request.url.path
    if path.startswith("/static") or path in ("/login", "/first-run"):
        return await call_next(request)
    # First-run choice if no env token and not decided yet
    if not AUTH_TOKEN and not WEB_SETTINGS.auth_decided():
        # Redirect everything (except static/login above) to first-run chooser
        return RedirectResponse(url="/first-run")
    # For SSE logs, let through and rely on middleware check below as HTML or JSON
    if not _is_authorized(request):
        # If HTML page, redirect to login; if API, return 401 JSON
        accept = request.headers.get("accept", "")
        if "text/html" in accept and not path.startswith("/api"):
            return RedirectResponse(url="/login")
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    return await call_next(request)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Build status snapshot
    statuses = tool_snapshot()
    return templates.TemplateResponse("index.html", {"request": request, "statuses": statuses})


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    # If no token configured, inform user that auth is disabled
    return templates.TemplateResponse("login.html", {"request": request, "enabled": bool(_current_token())})


@app.post("/login")
async def login(request: Request):
    token_cfg = _current_token()
    if not token_cfg:
        # Auth disabled; redirect to home
        return RedirectResponse("/", status_code=302)
    form = await request.form()
    raw = form.get("token")
    if isinstance(raw, bytes):
        token = raw.decode(errors="ignore")
    elif isinstance(raw, str):
        token = raw
    else:
        token = str(raw or "")
    token = token.strip()
    if token and token_cfg and token == token_cfg:
        resp = RedirectResponse("/", status_code=302)
        # session cookie, httpOnly for basic protection
        resp.set_cookie("x-auth", token_cfg, httponly=True, samesite="lax")
        return resp
    # invalid
    return templates.TemplateResponse("login.html", {"request": request, "enabled": True, "error": "Invalid token"}, status_code=401)


@app.get("/first-run", response_class=HTMLResponse)
async def first_run(request: Request):
    # If env token is set or auth already decided, skip
    if AUTH_TOKEN or WEB_SETTINGS.auth_decided():
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("first_run.html", {"request": request})


@app.post("/first-run")
async def first_run_post(request: Request):
    if AUTH_TOKEN or WEB_SETTINGS.auth_decided():
        return RedirectResponse("/", status_code=302)
    form = await request.form()
    raw_dec = form.get("decision")
    if isinstance(raw_dec, bytes):
        decision = raw_dec.decode(errors="ignore").strip().lower()
    elif isinstance(raw_dec, str):
        decision = raw_dec.strip().lower()
    else:
        decision = str(raw_dec or "").strip().lower()
    if decision == "skip":
        WEB_SETTINGS.set_auth(False)
        return RedirectResponse("/", status_code=302)
    # enable auth; allow custom token or generate one
    raw = form.get("token")
    if isinstance(raw, bytes):
        token = raw.decode(errors="ignore").strip()
    elif isinstance(raw, str):
        token = raw.strip()
    else:
        token = ""
    if not token:
        # Generate a simple random token
        import secrets
        token = secrets.token_urlsafe(24)
    WEB_SETTINGS.set_auth(True, token)
    # set cookie so user is immediately logged in
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie("x-auth", token, httponly=True, samesite="lax")
    return resp


@app.get("/tools", response_class=HTMLResponse)
async def tools_page(request: Request):
    statuses = tool_snapshot()
    return templates.TemplateResponse("tools.html", {"request": request, "statuses": statuses})


@app.get("/models", response_class=HTMLResponse)
async def models_page(request: Request):
    # Initial page, client fetches details via APIs
    return templates.TemplateResponse("models.html", {"request": request})


@app.get("/wizard", response_class=HTMLResponse)
async def wizard_form(request: Request):
    return templates.TemplateResponse("wizard.html", {"request": request})


@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    return templates.TemplateResponse("help.html", {"request": request})


# htmx partials
@app.get("/partials/tool-card/{tool}", response_class=HTMLResponse)
async def partial_tool_card(tool: str, request: Request):
    name = tool.lower()
    if name not in SUPPORTED_TOOLS:
        raise HTTPException(404, detail="Unknown tool")
    snap = tool_snapshot()
    s = snap.get(name)
    if not s:
        raise HTTPException(404, detail="No status")
    return templates.TemplateResponse("partials/tool_card.html", {"request": request, "name": name, "s": s})


@app.post("/wizard/run")
async def wizard_run(payload: dict):
    base_dir = payload.get("base_dir")
    venv_name = payload.get("venv_name")
    auto_link = payload.get("auto_link_models")
    # optionale Defaults
    default_host = (payload.get("default_host") or "").strip() or None
    default_port = payload.get("default_port")
    flags_tmpl = (payload.get("default_flags") or "").strip() or None

    if not base_dir:
        raise HTTPException(400, detail="base_dir erforderlich")

    def _wizard():
        # Persist config and run setup
        from ..core.config import save_config
        save_config(base_dir=Path(base_dir), venv_name=venv_name, auto_link_models=bool(auto_link))
        run_setup_wizard(base_dir=Path(base_dir), venv_name=venv_name, install_comfy=True)
        # Speichere Defaults in ToolsSettings
        defaults: dict[str, str] = {}
        if flags_tmpl or default_host or default_port:
            # Baue eine generische Extra-Args-Zeile aus Template
            # Erlaubt Platzhalter {host} und {port}
            host = default_host or "0.0.0.0"
            port = str(default_port) if default_port else ""
            if flags_tmpl:
                try:
                    extra = flags_tmpl.format(host=host, port=port)
                except Exception:
                    extra = flags_tmpl
            else:
                extra = ""
            defaults = {"extra_args": extra}
            if default_host:
                defaults["host"] = host
            if default_port:
                defaults["port"] = port
            TOOLS_SETTINGS.update("__defaults__", **defaults)

    job = await JOBS.create("wizard:run")
    steps = [("Setup Wizard", _wizard)]
    asyncio.create_task(JOBS.run_steps(job, steps))
    return JSONResponse({"ok": True, "job_id": job.id})


@app.post("/api/install/{tool}")
async def api_install(tool: str):
    tool = tool.lower()
    ops = SUPPORTED_TOOLS.get(tool)
    if not ops:
        raise HTTPException(404, detail="Unknown tool")
    job = await JOBS.create(f"install:{tool}")

    steps: list[tuple[str, Callable[[], Any]]] = []
    # Spezielle, transparente Schritte für SillyTavern
    if tool == "sillytavern":
        dest = get_base_dir() / "SillyTavern"

        def _ensure_repo():
            llm_tools.install_sillytavern()  # sichert Repo, führt ggf. npm install auch aus

        def _nvm_install():
            if not has_cmd("node"):
                run_bash("curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash", check=False)

        def _node_lts():
            run_bash("source ~/.nvm/nvm.sh || source ~/.bashrc; nvm install --lts; nvm use --lts", check=False)

        def _npm_install():
            run_bash(f"cd '{dest}' && npm install", check=False)

        steps = [
            ("Repository/Grundinstallation", _ensure_repo),
            ("NVM installieren (falls nötig)", _nvm_install),
            ("Node LTS aktivieren", _node_lts),
            ("npm install", _npm_install),
        ]
    else:
        # Generischer Ein-Schritt-Installer
        steps.append((f"Installiere {tool}", ops["install"]))

    asyncio.create_task(JOBS.run_steps(job, steps))
    return JSONResponse({"ok": True, "job_id": job.id})


@app.post("/api/start/{tool}")
async def api_start(tool: str, background: bool = True, payload: dict | None = None):
    tool = tool.lower()
    ops = SUPPORTED_TOOLS.get(tool)
    if not ops:
        raise HTTPException(404, detail="Unknown tool")
    try:
        # Resolve extra args from payload override or stored settings
        extra_args_str: str | None = None
        if isinstance(payload, dict) and "extra_args" in payload:
            extra_args_str = str(payload.get("extra_args") or "").strip() or None
        else:
            # Tool-spezifisch, sonst Defaults
            tool_cfg = TOOLS_SETTINGS.get(tool)
            extra_args_str = str(tool_cfg.get("extra_args") or "").strip() or None
            if not extra_args_str:
                extra_args_str = str(TOOLS_SETTINGS.get_defaults().get("extra_args") or "").strip() or None
        argv = shlex.split(extra_args_str) if extra_args_str else []

        def _call_with_args(fn: Callable, args: list[str]):
            try:
                sig = inspect.signature(fn)
                if any(p.kind == p.VAR_POSITIONAL for p in sig.parameters.values()):
                    return fn(*args)
                # if function takes no var-args, call without extras
                return fn()
            except Exception:
                # best-effort fallback
                return fn()

        if background and "start_bg" in ops:
            pid = _call_with_args(ops["start_bg"], argv)
            return JSONResponse({"ok": True, "pid": pid})
        elif "start" in ops:
            _call_with_args(ops["start"], argv)
            return JSONResponse({"ok": True})
        else:
            raise HTTPException(400, detail="Start nicht verfügbar für dieses Tool")
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/api/stop/{tool}")
async def api_stop(tool: str):
    tool = tool.lower()
    ops = SUPPORTED_TOOLS.get(tool)
    if not ops:
        raise HTTPException(404, detail="Unknown tool")
    try:
        if "stop" in ops:
            ops["stop"]()
            return JSONResponse({"ok": True})
        else:
            raise HTTPException(400, detail="Stop nicht verfügbar für dieses Tool")
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/api/status")
async def api_status():
    return JSONResponse(tool_snapshot())


# Tool Settings API
@app.get("/api/tools/{tool}/settings")
async def api_tool_settings_get(tool: str):
    tool = tool.lower()
    if tool not in SUPPORTED_TOOLS:
        raise HTTPException(404, detail="Unknown tool")
    return JSONResponse(TOOLS_SETTINGS.get(tool))


@app.post("/api/tools/{tool}/settings")
async def api_tool_settings_update(tool: str, payload: dict):
    tool = tool.lower()
    if tool not in SUPPORTED_TOOLS:
        raise HTTPException(404, detail="Unknown tool")
    url = payload.get("url") if isinstance(payload, dict) else None
    extra_args = payload.get("extra_args") if isinstance(payload, dict) else None
    # einfache Validierung
    if url:
        try:
            pr = urlparse(url)
            if pr.scheme not in ("http", "https") or not pr.netloc:
                raise ValueError()
        except Exception:
            raise HTTPException(400, detail="Ungültige URL")
    if extra_args and len(str(extra_args)) > 800:
        raise HTTPException(400, detail="Extra Args zu lang")
    updated = TOOLS_SETTINGS.update(tool, url=url, extra_args=extra_args)
    return JSONResponse({"ok": True, "settings": updated})


@app.get("/api/tools/settings")
async def api_tools_settings_all():
    return JSONResponse(TOOLS_SETTINGS.all())


@app.get("/api/logs/{tool}")
async def api_logs(tool: str):
    tool = tool.lower()
    ops = SUPPORTED_TOOLS.get(tool)
    if not ops:
        raise HTTPException(404, detail="Unknown tool")
    out_path, err_path = ops["logs"]()
    data = {
        "stdout": str(out_path) if out_path else None,
        "stderr": str(err_path) if err_path else None,
    }
    return JSONResponse(data)


@app.get("/api/logs/{tool}/stream")
async def api_logs_stream(tool: str):
    tool = tool.lower()
    ops = SUPPORTED_TOOLS.get(tool)
    if not ops:
        raise HTTPException(404, detail="Unknown tool")
    out_path, err_path = ops["logs"]()
    if not out_path and not err_path:
        raise HTTPException(404, detail="No logs")

    async def event_gen():
        # Simultanes tail -f auf stdout und stderr; sende Event-Typen "stdout"/"stderr"
        outs = Path(out_path) if out_path and Path(out_path).exists() else None
        errs = Path(err_path) if err_path and Path(err_path).exists() else None
        if not outs and not errs:
            yield "event: info\ndata: Keine Logs verfügbar\n\n"
            return
        f_out = open(outs, "r", encoding="utf-8", errors="ignore") if outs else None
        f_err = open(errs, "r", encoding="utf-8", errors="ignore") if errs else None
        try:
            if f_out: f_out.seek(0, 2)
            if f_err: f_err.seek(0, 2)
            while True:
                sent = False
                if f_out:
                    line = f_out.readline()
                    if line:
                        yield f"event: stdout\ndata: {line.rstrip()}\n\n"
                        sent = True
                if f_err:
                    line = f_err.readline()
                    if line:
                        yield f"event: stderr\ndata: {line.rstrip()}\n\n"
                        sent = True
                if not sent:
                    await asyncio.sleep(0.3)
        finally:
            try:
                if f_out: f_out.close()
            except Exception:
                pass
            try:
                if f_err: f_err.close()
            except Exception:
                pass

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@app.websocket("/ws/logs/{tool}")
async def ws_logs(websocket: WebSocket, tool: str):
    # Simple auth for WS: check cookie/header/query
    try:
        if AUTH_TOKEN:
            # Access to cookies requires accept first in Starlette, so perform a quick check via headers or query; fallback: accept and then validate cookie
            token_ok = False
            if websocket.headers.get("x-auth") == AUTH_TOKEN:
                token_ok = True
            else:
                # query params
                qp = dict((kv.split("=", 1) + [""])[:2] for kv in (websocket.url.query or "").split("&") if kv)
                if qp.get("token") == AUTH_TOKEN:
                    token_ok = True
            await websocket.accept()
            if not token_ok:
                # try cookie after accept
                if websocket.cookies.get("x-auth") == AUTH_TOKEN:
                    token_ok = True
            if not token_ok:
                await websocket.close(code=1008)
                return
        else:
            await websocket.accept()
    except Exception:
        await websocket.close(code=1008)
        return
    tool = tool.lower()
    ops = SUPPORTED_TOOLS.get(tool)
    if not ops:
        await websocket.close(code=1008)
        return
    out_path, err_path = ops["logs"]()
    outs = Path(out_path) if out_path and Path(out_path).exists() else None
    errs = Path(err_path) if err_path and Path(err_path).exists() else None
    regex: str | None = None

    async def matches(line: str) -> bool:
        if not regex:
            return True
        try:
            import re
            return bool(re.search(regex, line, re.I))
        except Exception:
            return True

    f_out = open(outs, "r", encoding="utf-8", errors="ignore") if outs else None
    f_err = open(errs, "r", encoding="utf-8", errors="ignore") if errs else None
    try:
        if f_out: f_out.seek(0, 2)
        if f_err: f_err.seek(0, 2)
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                # simple control messages: {"cmd":"filter","regex":"..."}
                import json
                try:
                    data = json.loads(msg)
                    if isinstance(data, dict) and data.get("cmd") == "filter":
                        regex = str(data.get("regex") or "").strip() or None
                except Exception:
                    pass
            except asyncio.TimeoutError:
                pass

            sent = False
            if f_out:
                line = f_out.readline()
                if line and await matches(line):
                    await websocket.send_json({"channel": "stdout", "line": line.rstrip()})
                    sent = True
            if f_err:
                line = f_err.readline()
                if line and await matches(line):
                    await websocket.send_json({"channel": "stderr", "line": line.rstrip()})
                    sent = True
            if not sent:
                await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        pass
    finally:
        try:
            if f_out: f_out.close()
        except Exception:
            pass
        try:
            if f_err: f_err.close()
        except Exception:
            pass


# Jobs API
@app.get("/api/jobs")
async def api_jobs_list():
    jobs = await JOBS.list()
    return JSONResponse([job.__dict__ for job in sorted(jobs, key=lambda j: j.created, reverse=True)])


@app.get("/api/jobs/{job_id}")
async def api_jobs_get(job_id: str):
    job = await JOBS.get(job_id)
    if not job:
        raise HTTPException(404)
    return JSONResponse(job.__dict__)


# Models API
@app.get("/api/models/where")
async def api_models_where():
    loc = models_core.where()
    return JSONResponse({k: str(v) for k, v in loc.items()})


@app.get("/api/models/index")
async def api_models_index():
    idx = models_index.load_index()
    items = [
        {
            "category": e.category,
            "path": e.path,
            "size": e.size,
        }
        for _, e in sorted(idx.items(), key=lambda kv: (kv[1].category, kv[1].path))
    ]
    return JSONResponse(items)


@app.post("/api/models/refresh")
async def api_models_refresh():
    job = await JOBS.create("models:refresh")
    steps = [("Index aktualisieren", models_index.refresh_index)]
    asyncio.create_task(JOBS.run_steps(job, steps))
    return JSONResponse({"ok": True, "job_id": job.id})


@app.post("/api/models/link/{tool}")
async def api_models_link(tool: str, adopt: bool = False):
    def _fn():
        models_core.link_tool(tool, adopt=adopt)
    job = await JOBS.create(f"models:link:{tool}")
    steps = [("Verknüpfe Modelle", _fn)]
    asyncio.create_task(JOBS.run_steps(job, steps))
    return JSONResponse({"ok": True, "job_id": job.id})


@app.post("/api/models/download/{preset}")
async def api_models_download(preset: str):
    if preset not in models_dl.PRESETS:
        raise HTTPException(404, detail="Unbekanntes Preset")
    def _fn():
        models_dl.install_preset(preset)
    job = await JOBS.create(f"models:download:{preset}")
    steps = [(f"Lade {preset}", _fn)]
    asyncio.create_task(JOBS.run_steps(job, steps))
    return JSONResponse({"ok": True, "job_id": job.id})


# Entrypoint

def run(host: str = "0.0.0.0", port: int = 8000):
    """Run the web server using uvicorn."""
    # Require running inside WSL2/Linux; avoid launching on native Windows by default
    if os.name == "nt" and not os.environ.get("ROCMWSL_ALLOW_WINDOWS"):
        msg = (
            "This Web UI is intended to run inside WSL2.\n"
            "Open your WSL distro and run: rocmwsl-web\n\n"
            "From PowerShell you can launch it in WSL with:\n"
            "  wsl -e bash -lc 'rocmwsl-web'\n\n"
            "To bypass this check (not recommended), set ROCMWSL_ALLOW_WINDOWS=1."
        )
        print(msg)
        raise SystemExit(1)
    import uvicorn
    uvicorn.run("rocm_wsl_ai.web.app:app", host=host, port=port, reload=False)
