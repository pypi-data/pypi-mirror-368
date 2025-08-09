from __future__ import annotations
import os
import signal
import sys
from pathlib import Path
from typing import Sequence
from .config import _config_path


def _runtime_dir() -> Path:
    base = _config_path().parent
    (base / "run").mkdir(parents=True, exist_ok=True)
    (base / "logs").mkdir(parents=True, exist_ok=True)
    return base


def _pid_file(name: str) -> Path:
    return _runtime_dir() / "run" / f"{name}.pid"


def _log_files(name: str) -> tuple[Path, Path]:
    base = _runtime_dir() / "logs"
    return base / f"{name}.out.log", base / f"{name}.err.log"


def start_background(name: str, cmd: Sequence[str], cwd: Path | None = None, env: dict | None = None) -> int:
    """Start a background process, write PID file, and return PID.

    If already running (PID file present and alive), returns existing PID.
    """
    pidf = _pid_file(name)
    if pidf.exists():
        try:
            pid = int(pidf.read_text().strip())
            if _pid_alive(pid):
                return pid
        except Exception:
            pass
        # stale PID
        try:
            pidf.unlink()
        except Exception:
            pass

    stdout_path, stderr_path = _log_files(name)
    stdout = open(stdout_path, "a", buffering=1)
    stderr = open(stderr_path, "a", buffering=1)

    creationflags = 0
    preexec_fn = None
    if os.name == "nt":
        # Detach on Windows
        creationflags = 0x00000008 | 0x00000200  # CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
    else:
        # Detach from terminal on POSIX
        import os as _os
        preexec_fn = _os.setsid  # type: ignore

    import subprocess
    proc = subprocess.Popen(
        list(cmd),
        cwd=str(cwd) if cwd else None,
        env=env,
        stdout=stdout,
        stderr=stderr,
        stdin=subprocess.DEVNULL,
        creationflags=creationflags,
        preexec_fn=preexec_fn,  # type: ignore[arg-type]
    )
    pidf.write_text(str(proc.pid))
    return proc.pid


def stop(name: str, sig: int = signal.SIGTERM, timeout: float = 5.0) -> bool:
    """Stop a background process by name. Returns True if stopped or not running."""
    pidf = _pid_file(name)
    if not pidf.exists():
        return True
    try:
        pid = int(pidf.read_text().strip())
    except Exception:
        try:
            pidf.unlink()
        except Exception:
            pass
        return True

    if not _pid_alive(pid):
        try:
            pidf.unlink()
        except Exception:
            pass
        return True

    try:
        if os.name == "nt":
            import subprocess
            subprocess.call(["taskkill", "/PID", str(pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Kill the whole process group
            os.killpg(pid, sig)
    except Exception:
        pass

    # Best-effort cleanup
    try:
        pidf.unlink()
    except Exception:
        pass
    return True


def status(name: str) -> tuple[bool, int | None]:
    pidf = _pid_file(name)
    if not pidf.exists():
        return False, None
    try:
        pid = int(pidf.read_text().strip())
    except Exception:
        return False, None
    return (_pid_alive(pid), pid if _pid_alive(pid) else None)


def logs_path(name: str) -> tuple[Path, Path]:
    return _log_files(name)


def _pid_alive(pid: int) -> bool:
    try:
        if os.name == "nt":
            # On Windows, try opening the process (best-effort skipped); assume alive if kill 0 equivalent not available
            return True
        else:
            os.kill(pid, 0)
            return True
    except Exception:
        return False
