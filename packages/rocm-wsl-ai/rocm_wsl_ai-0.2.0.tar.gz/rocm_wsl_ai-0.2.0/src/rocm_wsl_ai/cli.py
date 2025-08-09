from __future__ import annotations
import os
import shutil
import subprocess
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

app = typer.Typer(help="ROCm-WSL-AI: install and manage AMD ROCm + local AI tools on WSL2")
console = Console()
models_app = typer.Typer(help="Gemeinsame Modellablage verwalten")

def find_repo_root() -> Path:
    # 1) Explicit override via env var
    env_root = os.environ.get("ROCM_WSL_AI_ROOT")
    if env_root:
        p = Path(env_root).expanduser().resolve()
        if (p / "pyproject.toml").exists() or (p / "src" / "rocm_wsl_ai").exists():
            return p
    # 2) Search from CWD upwards for a project root marker
    cur = Path.cwd().resolve()
    for parent in [cur] + list(cur.parents):
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    # 3) Fallback to package root (installed from source)
    pkg_root = Path(__file__).resolve().parents[2]
    return pkg_root if pkg_root.exists() else cur

ROOT = find_repo_root()


@app.command()
def install(
    target: str = typer.Argument(..., help="What to install: base|comfyui|sdnext|fooocus|textgen|forge|llama.cpp|koboldcpp|fastchat|ollama|sillytavern|all"),
):
    """Install a component (Python-native)."""
    t = target.lower()
    if t == "base":
        from .core.base import setup_rocm_and_pytorch_nightly
        setup_rocm_and_pytorch_nightly()
        raise typer.Exit(code=0)
    if t == "comfyui":
        from .tools.image import install_comfyui
        install_comfyui(); raise typer.Exit(code=0)
    if t == "sdnext":
        from .tools.image import install_sdnext
        install_sdnext(); raise typer.Exit(code=0)
    if t == "fooocus":
        from .tools.image import install_fooocus
        install_fooocus(); raise typer.Exit(code=0)
    if t in ("forge",):
        from .tools.image import install_forge
        install_forge(); raise typer.Exit(code=0)
    if t in ("a1111", "automatic1111"):
        from .tools.image import install_a1111
        install_a1111(); raise typer.Exit(code=0)
    if t in ("invokeai",):
        from .tools.image import install_invokeai
        install_invokeai(); raise typer.Exit(code=0)
    if t in ("textgen",):
        from .tools.llm import install_textgen
        install_textgen(); raise typer.Exit(code=0)
    if t in ("llama.cpp", "llama_cpp"):
        from .tools.llm import install_llama_cpp
        install_llama_cpp(); raise typer.Exit(code=0)
    if t == "koboldcpp":
        from .tools.llm import install_koboldcpp
        install_koboldcpp(); raise typer.Exit(code=0)
    if t == "fastchat":
        from .tools.llm import install_fastchat
        install_fastchat(); raise typer.Exit(code=0)
    if t == "ollama":
        from .tools.llm import install_ollama
        install_ollama(); raise typer.Exit(code=0)
    if t == "sillytavern":
        from .tools.llm import install_sillytavern
        install_sillytavern(); raise typer.Exit(code=0)
    if t == "all":
        # Install base plus a curated set
        from .core.base import setup_rocm_and_pytorch_nightly
        from .tools.image import install_comfyui
        setup_rocm_and_pytorch_nightly()
        install_comfyui()
        console.print("[green]Base + ComfyUI installed. Add others as needed with 'install <name>'.[/green]")
        raise typer.Exit(code=0)

    console.print("[red]Unknown target[/red]")
    raise typer.Exit(code=2)


@app.command()
def start(target: str = typer.Argument(..., help="Start a tool: comfyui")):
    t = target.lower()
    if t == "comfyui":
        from .tools.image import start_comfyui
        start_comfyui(); raise typer.Exit(code=0)
    if t == "sillytavern":
        from .tools.llm import start_sillytavern
        start_sillytavern(); raise typer.Exit(code=0)
    console.print("[red]Unknown start target[/red]")
    raise typer.Exit(code=2)


@app.command()
def start_bg(target: str = typer.Argument(..., help="Start tool im Hintergrund: comfyui")):
    t = target.lower()
    if t == "comfyui":
        from .tools.image import start_comfyui_background
        pid = start_comfyui_background()
        console.print(f"[green]ComfyUI gestartet (PID {pid}). Logs: rocmwsl logs comfyui[/green]")
        raise typer.Exit(code=0)
    if t == "sillytavern":
        from .tools.llm import start_sillytavern_background
        pid = start_sillytavern_background()
        console.print(f"[green]SillyTavern gestartet (PID {pid}).[/green]")
        raise typer.Exit(code=0)
    console.print("[red]Unknown start target[/red]")
    raise typer.Exit(code=2)


@app.command()
def stop(target: str = typer.Argument(..., help="Stoppe ein Tool: comfyui")):
    t = target.lower()
    if t == "comfyui":
        from .core import process
        process.stop("comfyui")
        console.print("[green]ComfyUI gestoppt.[/green]")
        raise typer.Exit(code=0)
    console.print("[red]Unknown stop target[/red]")
    raise typer.Exit(code=2)


@app.command()
def ps(target: str = typer.Argument("all", help="Status: all|comfyui")):
    from .core import process
    table = Table(title="Prozesse")
    table.add_column("Name")
    table.add_column("Running")
    table.add_column("PID")
    items = ["comfyui"] if target != "all" else ["comfyui"]
    for name in items:
        alive, pid = process.status(name)
        table.add_row(name, "yes" if alive else "no", str(pid or "-"))
    console.print(table)


@app.command()
def logs(target: str = typer.Argument(..., help="Logs anzeigen: comfyui")):
    from .core import process
    out, err = process.logs_path(target)
    console.print(f"stdout: {out}")
    console.print(f"stderr: {err}")


@app.command()
def update(
    target: str = typer.Argument(
        "all",
        help="What to update: all|self|base|comfyui|sdnext|fooocus|forge|a1111|invokeai|textgen|llama.cpp|koboldcpp|fastchat|ollama",
    )
):
    """Update one or all components.

    - self: upgrade this CLI/TUI (prefers pipx, falls back to pip)
    - base: refresh PyTorch Nightly in the venv
    - tools: git pull (and minimal deps where relevant)
    - all: self + base + all tools
    """
    from .core.utils import git_pull_if_exists
    from .core import venv

    t = target.lower()

    def update_self():
        # Try pipx first (most common install path), else fallback to pip inside current env
        if shutil.which("pipx"):
            console.print("[cyan]Upgrading via pipx...[/cyan]")
            rc = subprocess.call(["pipx", "upgrade", "rocm-wsl-ai"])  # legacy name kept
            # also upgrade the short alias if present
            subprocess.call(["pipx", "upgrade", "rocmwsl"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if rc == 0:
                console.print("[green]CLI/TUI upgraded via pipx.[/green]")
                return
        # Fallback
        console.print("[cyan]Upgrading via pip (fallback)...[/cyan]")
        subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "rocm-wsl-ai"])

    def update_base():
        # Reinstall PyTorch Nightly into venv (ROCm-preferred, fallback CPU)
        from .core.base import install_pytorch_nightly
        try:
            install_pytorch_nightly(rocm_preferred=True)
        except Exception:
            install_pytorch_nightly(rocm_preferred=False)
        console.print("[green]Base updated (PyTorch Nightly).")

    def update_git_dir(path: Path, name: str):
        if git_pull_if_exists(path):
            console.print(f"[green]{name} updated.[/green]")
        else:
            console.print(f"[yellow]{name} not found, install first.[/yellow]")

    HOME = Path.home()
    locations = {
        "comfyui": HOME / "ComfyUI",
        "sdnext": HOME / "SD.Next",
        "fooocus": HOME / "Fooocus",
        "forge": HOME / "stable-diffusion-webui-forge",
        "a1111": HOME / "stable-diffusion-webui",
        "textgen": HOME / "text-generation-webui",
        "llama.cpp": HOME / "llama.cpp",
        "koboldcpp": HOME / "KoboldCpp",
        # fastchat via pip; no repo path by default
    }

    if t == "self":
        update_self(); raise typer.Exit(code=0)

    if t == "base":
        update_base(); raise typer.Exit(code=0)

    if t in locations:
        update_git_dir(locations[t], t); raise typer.Exit(code=0)

    if t == "fastchat":
        # pip package
        venv.ensure(); venv.pip_install(["--upgrade", "fschat"]); console.print("[green]FastChat upgraded.[/green]"); raise typer.Exit(code=0)

    if t == "invokeai":
        venv.ensure(); venv.pip_install(["--upgrade", "InvokeAI"]); console.print("[green]InvokeAI upgraded.[/green]"); raise typer.Exit(code=0)

    if t == "ollama":
        console.print("[yellow]Update Ollama via official installer or apt; automation pending.[/yellow]"); raise typer.Exit(code=0)

    if t == "all":
        update_self()
        update_base()
        for key, path in locations.items():
            if key in ("invokeai",):
                venv.ensure(); venv.pip_install(["--upgrade", "InvokeAI"])
            else:
                update_git_dir(path, key)
        # extras
        venv.ensure(); venv.pip_install(["--upgrade", "fschat"])  # fastchat
        console.print("[green]All updates complete.[/green]")
        raise typer.Exit(code=0)

    console.print("[red]Unknown update target[/red]")
    raise typer.Exit(code=2)


@app.command()
def menu():
    """Open the new Textual TUI."""
    from .tui.app import run as tui_run
    tui_run()
    raise typer.Exit(code=0)


@app.command()
def web(
    host: str = typer.Option("0.0.0.0", "--host", help="Bind-Adresse"),
    port: int = typer.Option(8000, "--port", help="Port"),
):
    """Starte das Web-Interface (FastAPI)."""
    try:
        from .web.app import run as web_run
    except Exception as e:
        console.print("[red]Web-Komponenten fehlen. Installiere Abhängigkeiten: fastapi, uvicorn, jinja2.[/red]")
        console.print(str(e))
        raise typer.Exit(code=2)
    web_run(host=host, port=port)


@app.command()
def wizard(
    base_dir: Optional[Path] = typer.Option(None, "--base-dir", help="Installations-Basisverzeichnis"),
    venv_name: Optional[str] = typer.Option(None, "--venv-name", help="Name der Python-Venv"),
    no_comfy: bool = typer.Option(False, "--no-comfy", help="ComfyUI nicht automatisch installieren"),
):
    """Geführtes Setup: Konfiguriert, prüft und installiert Base (+ optional ComfyUI)."""
    from .core.base import run_setup_wizard
    run_setup_wizard(base_dir=base_dir, venv_name=venv_name, install_comfy=not no_comfy)
    console.print("[green]Setup abgeschlossen. Nutze 'rocmwsl start comfyui' zum Start.[/green]")
    raise typer.Exit(code=0)


@app.command("list")
def list_cmd():
    """List available components."""
    table = Table(title="ROCm-WSL-AI Components")
    table.add_column("Target")
    table.add_column("Type")
    items = [
        ("base", "system"),
        ("comfyui", "image"),
        ("sdnext", "image"),
        ("fooocus", "image"),
        ("forge", "image"),
        ("a1111", "image"),
        ("invokeai", "image"),
        ("textgen", "llm"),
        ("llama.cpp", "llm"),
        ("koboldcpp", "llm"),
        ("fastchat", "llm"),
        ("ollama", "llm"),
    ("sillytavern", "chat-ui"),
    ]
    for k, t in items:
        table.add_row(k, t)
    console.print(table)


@models_app.command("init")
def models_init():
    from .core.models import ensure_store, where
    ensure_store()
    loc = where()
    console.print(f"[green]Model Store initialisiert:[/green] {loc['store']}")


@models_app.command("link")
def models_link(tool: str = typer.Argument(..., help="Tool: comfyui|sdnext|forge|a1111|textgen|llama.cpp|koboldcpp"), adopt: bool = typer.Option(False, "--adopt", help="Vorhandene Dateien in Store verschieben")):
    from .core.models import link_tool
    res = link_tool(tool, adopt=adopt)
    table = Table(title=f"Model-Linking: {tool}")
    table.add_column("Store")
    table.add_column("Tool Path")
    table.add_column("OK")
    table.add_column("Info")
    for target, link, ok, msg in res:
        table.add_row(str(target), str(link), "yes" if ok else "no", msg)
    console.print(table)


@models_app.command("adopt")
def models_adopt(tool: str = typer.Argument(..., help="Wie link, aber verschiebe vorhandene Dateien in Store")):
    from .core.models import link_tool
    res = link_tool(tool, adopt=True)
    table = Table(title=f"Model-Adopt: {tool}")
    table.add_column("Store")
    table.add_column("Tool Path")
    table.add_column("OK")
    table.add_column("Info")
    for target, link, ok, msg in res:
        table.add_row(str(target), str(link), "yes" if ok else "no", msg)
    console.print(table)


@models_app.command("where")
def models_where():
    from .core.models import where
    loc = where()
    table = Table(title="Model Store")
    table.add_column("Name")
    table.add_column("Pfad")
    for k, v in loc.items():
        console.print(f"{k}: {v}")


@models_app.command("refresh")
def models_refresh():
    from .core.models_index import refresh_index
    idx = refresh_index()
    console.print(f"[green]Index aktualisiert:[/green] {len(idx)} Modelle")


@models_app.command("list")
def models_list():
    from .core.models_index import load_index
    idx = load_index()
    table = Table(title="Modelle")
    table.add_column("Kategorie")
    table.add_column("Pfad")
    table.add_column("Größe")
    for _, e in sorted(idx.items(), key=lambda kv: (kv[1].category, kv[1].path)):
        table.add_row(e.category, e.path, f"{e.size/1024/1024:.1f} MB")
    console.print(table)


@models_app.command("inspect")
def models_inspect(path: Path = typer.Argument(..., help="Pfad zur Modelldatei"), hash: bool = typer.Option(False, "--hash", help="SHA256 berechnen")):
    from .core.models_index import compute_sha256
    if not path.exists():
        console.print("[red]Datei nicht gefunden[/red]")
        raise typer.Exit(code=2)
    table = Table(title="Modell-Infos")
    table.add_column("Attribut")
    table.add_column("Wert")
    st = path.stat()
    table.add_row("Pfad", str(path))
    table.add_row("Größe", f"{st.st_size/1024/1024:.2f} MB")
    if hash:
        table.add_row("SHA256", compute_sha256(path))
    console.print(table)


@models_app.command("download")
def models_download(preset: str = typer.Argument(..., help="Preset-Name")):
    from .core.models_download import PRESETS, install_preset, preset_path
    if preset not in PRESETS:
        console.print("[red]Unbekanntes Preset[/red]")
        raise typer.Exit(code=2)
    size = PRESETS[preset].get("size")
    if size:
        console.print(f"[cyan]Hinweis Größe:[/cyan] {size}")
    dest = install_preset(preset)
    console.print(f"[green]Geladen:[/green] {dest}")


@models_app.command("download-many")
def models_download_many(presets: list[str] = typer.Argument(..., help="Mehrere Presets"), parallel: int = typer.Option(3, "--parallel")):
    from .core.models_download import PRESETS, install_presets
    for p in presets:
        if p not in PRESETS:
            console.print(f"[red]Unbekanntes Preset:[/red] {p}")
            raise typer.Exit(code=2)
    console.print("[cyan]Größenhinweise:[/cyan] " + ", ".join(f"{p}:{PRESETS[p].get('size','-')}" for p in presets))
    paths = install_presets(presets, parallel=parallel)
    console.print(f"[green]Fertig:[/green] {len(paths)} Dateien")


@models_app.command("presets")
def models_presets():
    from .core.models_download import PRESETS
    table = Table(title="Model-Presets")
    table.add_column("Name")
    table.add_column("Kategorie")
    table.add_column("Datei")
    table.add_column("Größe")
    for name, spec in PRESETS.items():
        table.add_row(name, spec.get("category", "-"), spec.get("filename", "-"), spec.get("size", "-"))
    console.print(table)


@models_app.command("rm")
def models_rm(path: Path = typer.Argument(..., help="Pfad zur Modelldatei")):
    if not path.exists():
        console.print("[yellow]Nicht vorhanden[/yellow]")
        raise typer.Exit(code=0)
    path.unlink()
    console.print("[green]Gelöscht.[/green]")


app.add_typer(models_app, name="models")


@app.command()
def status():
    """Quick status: ROCm tools, PyTorch, and installed folders."""
    table = Table(title="Status")
    table.add_column("Check")
    table.add_column("Result")

    # ROCm tools
    def has(cmd: str) -> bool:
        return shutil.which(cmd) is not None

    table.add_row("rocminfo", "yes" if has("rocminfo") else "no")
    table.add_row("rocm-smi", "yes" if has("rocm-smi") else "no")

    # PyTorch + ROCm in venv if present
    from .core.venv import PYTHON as VENV_PY, VENV_NAME as VENV_NAME
    if VENV_PY.exists():
        try:
            out = subprocess.check_output([str(VENV_PY), "-c", "import torch;print(torch.__version__);print(torch.cuda.is_available())"], text=True)
            lines = [l.strip() for l in out.strip().splitlines()]
            if len(lines) >= 2:
                table.add_row("PyTorch", lines[0])
                table.add_row("torch.cuda.is_available()", lines[1])
        except Exception as e:
            table.add_row("PyTorch", f"error: {e}")
    else:
        table.add_row(f"venv ({VENV_NAME})", "missing")

    # Installed folders
    from .core.config import get_base_dir
    BASE = get_base_dir()
    installs = {
        "ComfyUI": BASE / "ComfyUI",
        "SD.Next": BASE / "SD.Next",
        "Fooocus": BASE / "Fooocus",
        "Forge": BASE / "stable-diffusion-webui-forge",
        "A1111": BASE / "stable-diffusion-webui",
        "TextGenWebUI": BASE / "text-generation-webui",
        "llama.cpp": BASE / "llama.cpp",
        "KoboldCpp": BASE / "KoboldCpp",
    }
    for name, path in installs.items():
        table.add_row(name, "installed" if path.exists() else "-")

    console.print(table)


@app.command()
def doctor():
    """Run diagnostics to help troubleshoot common issues."""
    from .core.utils import output, has_cmd
    from .core.venv import PYTHON as VENV_PY

    table = Table(title="Doctor")
    table.add_column("Probe")
    table.add_column("Result")

    # WSL GPU visibility
    kfd = Path("/dev/kfd").exists()
    dri = Path("/dev/dri").exists()
    table.add_row("/dev/kfd", "present" if kfd else "missing (WSL: GPU-Freigabe aktivieren, ggf. Treiber updaten)")
    table.add_row("/dev/dri", "present" if dri else "missing (WSL: render/video Gruppen + Neustart)")

    # rocm tools
    for tool in ("rocminfo", "rocm-smi"):
        if has_cmd(tool):
            ver = output([tool, "--version"]) or "yes"
            table.add_row(tool, ver)
        else:
            table.add_row(tool, "no (installiere ROCm Tools / apt repo prüfen)")

    # Python and Torch
    if VENV_PY.exists():
        torch_test = (
            "import torch; print('torch', torch.__version__); "
            "print('cuda?', torch.cuda.is_available()); "
            "print('hip?', getattr(torch.version, 'hip', None))"
        )
        try:
            out = subprocess.check_output([str(VENV_PY), "-c", torch_test], text=True)
            for line in out.strip().splitlines():
                k, v = line.split(" ", 1) if " " in line else ("info", line)
                table.add_row(k, v)
        except Exception as e:
            table.add_row("torch", f"error: {e} (rocmwsl update base oder wizard erneut ausführen)")
    else:
        table.add_row("venv", "missing (rocmwsl wizard oder rocmwsl install base)")

    console.print(table)


@app.command()
def remove(target: str = typer.Argument(..., help="Remove a tool: comfyui|sdnext"), force: bool = typer.Option(False, "--force", help="Skip confirmation")):
    mapping = {
        "comfyui": Path.home() / "ComfyUI",
        "sdnext": Path.home() / "SD.Next",
    }
    key = target.lower()
    if key not in mapping:
        console.print("[red]Unknown remove target[/red]")
        raise typer.Exit(code=2)
    path = mapping[key]
    if not path.exists():
        console.print("[yellow]Nothing to remove.[/yellow]")
        raise typer.Exit(code=0)
    if not force:
        proceed = typer.confirm(f"Remove '{path}'? This deletes files.")
        if not proceed:
            raise typer.Exit(code=0)
    shutil.rmtree(path)
    console.print(f"[green]Removed:[/green] {path}")


if __name__ == "__main__":
    app()
