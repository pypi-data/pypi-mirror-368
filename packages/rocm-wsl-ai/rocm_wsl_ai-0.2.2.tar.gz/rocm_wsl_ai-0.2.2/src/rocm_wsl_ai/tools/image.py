from __future__ import annotations
from pathlib import Path
from ..core import venv
from ..core.utils import git_clone_or_pull, run
from ..core import process
from ..core.config import get_base_dir, get_auto_link_models
from ..core.models import link_tool

BASE = get_base_dir()


def install_comfyui():
    venv.ensure()
    dest = BASE / "ComfyUI"
    git_clone_or_pull("https://github.com/comfyanonymous/ComfyUI.git", dest)
    # optional: comfyui manager
    manager_dir = dest / "custom_nodes" / "ComfyUI-Manager"
    git_clone_or_pull("https://github.com/ltdrdata/ComfyUI-Manager.git", manager_dir)
    # Dependencies
    req = dest / "requirements.txt"
    venv.pip_install(["setuptools", "wheel"])  # common build deps
    from ..core.venv import pip_install_requirements
    pip_install_requirements(req)
    if get_auto_link_models():
        link_tool("comfyui", adopt=False)


def start_comfyui(*args: str):
    dest = BASE / "ComfyUI"
    main = dest / "main.py"
    venv.ensure()
    cmd = [str(venv.python()), str(main), *args]
    if get_auto_link_models():
        link_tool("comfyui", adopt=False)
    run(cmd)


def start_comfyui_background(*args: str) -> int:
    dest = BASE / "ComfyUI"
    main = dest / "main.py"
    venv.ensure()
    cmd = [str(venv.python()), str(main), *args]
    return process.start_background("comfyui", cmd, cwd=dest)


def install_sdnext():
    venv.ensure()
    dest = BASE / "SD.Next"
    git_clone_or_pull("https://github.com/vladmandic/sdnext.git", dest)
    # Dependencies will be handled by sdnext on first start; preinstall basics
    venv.pip_install(["fastapi", "uvicorn"])  # light touch
    if get_auto_link_models():
        link_tool("sdnext", adopt=False)


def _bash_bg(name: str, dest: Path, script: str = "webui.sh") -> int:
    # Start a bash-based script in background (WSL/Linux)
    cmd = [
        "bash", "-lc",
        f"cd '{dest}'; chmod +x ./{script} || true; ./{script}"
    ]
    return process.start_background(name, cmd, cwd=dest)


def install_fooocus():
    venv.ensure()
    dest = BASE / "Fooocus"
    git_clone_or_pull("https://github.com/lllyasviel/Fooocus.git", dest)
    from ..core.venv import pip_install_requirements
    pip_install_requirements(dest / "requirements_versions.txt")
    if get_auto_link_models():
        link_tool("comfyui", adopt=False)  # Fooocus verwendet ähnliche Ordner (optional)


def start_fooocus_background(*args: str) -> int:
    dest = BASE / "Fooocus"
    main = dest / "launch.py"
    venv.ensure()
    cmd = [str(venv.python()), str(main), *args]
    return process.start_background("fooocus", cmd, cwd=dest)


def install_forge():
    venv.ensure()
    dest = BASE / "stable-diffusion-webui-forge"
    git_clone_or_pull("https://github.com/lllyasviel/stable-diffusion-webui-forge.git", dest)
    # webui.sh is bash; dependencies will resolve on first run. Preinstall torch later via base.
    if get_auto_link_models():
        link_tool("forge", adopt=False)


def start_sdnext_background(*args: str) -> int:
    dest = BASE / "SD.Next"
    return _bash_bg("sdnext", dest, script="webui.sh")


def start_a1111_background(*args: str) -> int:
    dest = BASE / "stable-diffusion-webui"
    return _bash_bg("a1111", dest, script="webui.sh")


def start_forge_background(*args: str) -> int:
    dest = BASE / "stable-diffusion-webui-forge"
    return _bash_bg("forge", dest, script="webui.sh")


def install_a1111():
    venv.ensure()
    dest = BASE / "stable-diffusion-webui"
    git_clone_or_pull("https://github.com/AUTOMATIC1111/stable-diffusion-webui.git", dest)
    # Dependencies handled by the project; base installs torch.
    if get_auto_link_models():
        link_tool("a1111", adopt=False)


def install_invokeai():
    venv.ensure()
    venv.pip_install(["InvokeAI>=4.0.0b0"])  # use current invokeai package
    # no linking


def start_invokeai_background(*args: str) -> int:
    # Run InvokeAI server or TUI (default); expose logs via process
    venv.ensure()
    cmd = [str(venv.python()), "-m", "invokeai"]
    return process.start_background("invokeai", cmd)
