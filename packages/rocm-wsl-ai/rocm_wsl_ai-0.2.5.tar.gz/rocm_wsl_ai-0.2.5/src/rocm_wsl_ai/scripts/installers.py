from __future__ import annotations
from pathlib import Path
import subprocess
from rich.console import Console

console = Console()
HOME = Path.home()
VENV = HOME / "genai_env" / "bin"


def ensure_base():
    script = Path("1_setup_pytorch_rocm_wsl.sh")
    if script.exists():
        return subprocess.call(["bash", str(script)])
    console.print("[red]Base setup script missing.[/red]")
    return 2


def install_comfyui():
    script = Path("2_install_comfyui.sh")
    if script.exists():
        return subprocess.call(["bash", str(script)])
    return 2


def start_comfyui(*args: str):
    script = Path("3_start_comfyui.sh")
    if script.exists():
        return subprocess.call(["bash", str(script), *args])
    return 2


def install_sdnext():
    script = Path("4_install_sdnext.sh")
    if script.exists():
        return subprocess.call(["bash", str(script)])
    return 2


def update_all():
    script = Path("5_update_ai_setup.sh")
    if script.exists():
        return subprocess.call(["bash", str(script)])
    return 0
