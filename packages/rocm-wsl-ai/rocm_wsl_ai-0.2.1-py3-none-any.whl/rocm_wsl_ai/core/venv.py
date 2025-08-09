from __future__ import annotations
from pathlib import Path
from typing import Sequence
from .utils import run
from .config import get_venv_name

HOME = Path.home()
VENV_NAME = get_venv_name()
VENV_DIR = HOME / VENV_NAME
# Support both POSIX and Windows venv layout
BIN = VENV_DIR / ("Scripts" if (VENV_DIR / "Scripts").exists() else "bin")
PYTHON = BIN / ("python.exe" if (BIN / "python.exe").exists() else "python")
PIP = BIN / ("pip.exe" if (BIN / "pip.exe").exists() else "pip")


def ensure() -> None:
    if not PYTHON.exists():
        run(["python3", "-m", "venv", str(VENV_DIR)], check=True)
        run([str(PIP), "install", "--upgrade", "pip"], check=True)


def pip_install(packages: Sequence[str], extra_index_url: str | None = None) -> None:
    cmd = [str(PIP), "install", *packages]
    if extra_index_url:
        cmd += ["--extra-index-url", extra_index_url]
    run(cmd, check=True)


def python() -> Path:
    return PYTHON


def pip_install_requirements(req_file: Path) -> None:
    if not req_file.exists():
        return
    run([str(PIP), "install", "-r", str(req_file)], check=True)
