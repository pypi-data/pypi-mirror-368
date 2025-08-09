from __future__ import annotations
from pathlib import Path
from ..core import venv
from ..core.utils import git_clone_or_pull, run, has_cmd, run_bash
from ..core import process
from ..core.config import get_base_dir
from ..core.config import get_auto_link_models
from ..core.models import link_tool

BASE = get_base_dir()


def install_textgen():
    venv.ensure()
    dest = BASE / "text-generation-webui"
    git_clone_or_pull("https://github.com/oobabooga/text-generation-webui.git", dest)
    from ..core.venv import pip_install_requirements
    pip_install_requirements(dest / "requirements.txt")
    if get_auto_link_models():
        link_tool("textgen", adopt=False)


def start_textgen_background(*args: str) -> int:
    dest = BASE / "text-generation-webui"
    # Launch script variant
    script = dest / "oneclick.py"
    if not script.exists():
        script = dest / "launch.py"
    cmd = [str(venv.python()), str(script), *args]
    return process.start_background("textgen", cmd, cwd=dest)


def install_llama_cpp():
    dest = BASE / "llama.cpp"
    git_clone_or_pull("https://github.com/ggerganov/llama.cpp.git", dest)
    # Minimal build (CPU), ROCm build is environment-specific, keep optional
    run(["make"], cwd=dest)
    if get_auto_link_models():
        link_tool("llama.cpp", adopt=False)


def start_llama_cpp_background(*args: str) -> int:
    dest = BASE / "llama.cpp"
    binary = dest / "main"
    if not binary.exists():
        binary = dest / "build" / "bin" / "main"
    cmd = [str(binary), *args] if binary.exists() else ["bash", "-lc", f"cd '{dest}'; make; ./main"]
    return process.start_background("llama.cpp", cmd, cwd=dest)


def install_koboldcpp():
    dest = BASE / "KoboldCpp"
    git_clone_or_pull("https://github.com/LostRuins/koboldcpp.git", dest)
    # Build defaults (CPU); ROCm/HIP optional
    run(["make"], cwd=dest)
    if get_auto_link_models():
        link_tool("koboldcpp", adopt=False)


def start_koboldcpp_background(*args: str) -> int:
    dest = BASE / "KoboldCpp"
    binary = dest / "koboldcpp"
    cmd = [str(binary), *args] if binary.exists() else ["bash", "-lc", f"cd '{dest}'; make; ./koboldcpp"]
    return process.start_background("koboldcpp", cmd, cwd=dest)


def install_fastchat():
    venv.ensure()
    venv.pip_install(["fschat"])


def install_ollama():
    # Install via official script if present or apt repo; for now, print hint
    from ..core.utils import console
    console.print("[yellow]Please install Ollama via their official instructions for WSL/systemd. Future versions will automate this.[/yellow]")


def start_fastchat_background(*args: str) -> int:
    # Start the legacy Gradio web server from FastChat (simple all-in-one)
    # Users can override host/port via Extra Args: e.g., --host 0.0.0.0 --port 7861
    venv.ensure()
    cmd = [str(venv.python()), "-m", "fastchat.serve.gradio_web_server", *args]
    return process.start_background("fastchat", cmd)


def start_ollama_background(*args: str) -> int:
    # Start Ollama local server (requires system installation). Bind to all interfaces if possible.
    # Extra args are ignored for now; users can configure OLLAMA_HOST via environment if needed.
    cmd = ["bash", "-lc", "OLLAMA_HOST=0.0.0.0 ollama serve"]
    return process.start_background("ollama", cmd)


def install_sillytavern():
    venv.ensure()
    dest = BASE / "SillyTavern"
    git_clone_or_pull("https://github.com/SillyTavern/SillyTavern.git", dest)
    # Automatisches Node.js-Setup via nvm (falls node fehlt)
    if not has_cmd("node"):
        run_bash("curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash", check=False)
        # lade nvm in Login-Shell und installiere LTS
        run_bash("source ~/.nvm/nvm.sh || source ~/.bashrc; nvm install --lts; nvm use --lts", check=False)
    # Abhängigkeiten installieren
    run_bash(f"cd '{dest}' && npm install", check=False)
    from ..core.utils import console
    console.print("[green]SillyTavern bereit. Starte mit 'rocmwsl start sillytavern'.[/green]")


def start_sillytavern():
    dest = BASE / "SillyTavern"
    if not dest.exists():
        from ..core.utils import console
        console.print("[red]SillyTavern nicht installiert.[/red]")
        return
    # Stelle sicher, dass node verfügbar ist (nvm)
    run_bash("source ~/.nvm/nvm.sh || source ~/.bashrc; nvm use --lts || true", check=False)
    run_bash(f"cd '{dest}' && npm run start", check=False)


def start_sillytavern_background() -> int:
    dest = BASE / "SillyTavern"
    if not dest.exists():
        from ..core.utils import console
        console.print("[red]SillyTavern nicht installiert.[/red]")
        return -1
    cmd = [
        "bash", "-lc",
        f"source ~/.nvm/nvm.sh || source ~/.bashrc; nvm use --lts || true; cd '{dest}'; npm run start"
    ]
    return process.start_background("sillytavern", cmd, cwd=dest)
