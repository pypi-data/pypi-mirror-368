from __future__ import annotations
import os
import subprocess
from pathlib import Path
from typing import Sequence
from rich.console import Console
import shutil

console = Console()


def run(cmd: Sequence[str], cwd: Path | None = None, env: dict | None = None, check: bool = False) -> int:
    """Run a subprocess command with pretty printing."""
    console.print(f"[cyan]$ {' '.join(cmd)}[/cyan]")
    rc = subprocess.call(cmd, cwd=str(cwd) if cwd else None, env=env)
    if check and rc != 0:
        raise RuntimeError(f"Command failed with code {rc}: {' '.join(cmd)}")
    return rc


def ensure_packages(pkgs: list[str]):
    """Install apt packages with sudo if available (WSL-safe)."""
    sudo = "sudo" if os.environ.get("SUDO_USER") or os.environ.get("WSL_DISTRO_NAME") else None
    cmd = ([sudo] if sudo else []) + ["apt", "update"]
    run(cmd)
    cmd = ([sudo] if sudo else []) + ["apt", "install", "-y", *pkgs]
    run(cmd, check=True)


def git_clone_or_pull(url: str, dest: Path) -> None:
    if dest.exists():
        run(["git", "-C", str(dest), "pull", "--rebase"])
    else:
        run(["git", "clone", url, str(dest)], check=True)


def git_pull_if_exists(dest: Path) -> bool:
    """If a git repo dir exists, pull rebase. Returns True if pulled, False if skipped."""
    if dest.exists() and dest.is_dir():
        run(["git", "-C", str(dest), "pull", "--rebase"])
        return True
    return False


def output(cmd: Sequence[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True).strip()
    except Exception:
        return ""


def has_cmd(cmd: str) -> bool:
    """Return True if command is resolvable in PATH."""
    return shutil.which(cmd) is not None


def run_bash(command: str, check: bool = False) -> int:
    """Run a bash -lc '...' command (useful for nvm/npm flows).

    On non-POSIX systems this requires bash availability (WSL expected).
    """
    return run(["bash", "-lc", command], check=check)
