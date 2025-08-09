from __future__ import annotations
from pathlib import Path
from .utils import ensure_packages, run, output, has_cmd
from . import venv


def _detect_rocm_series() -> str | None:
    """Try to infer ROCm series (e.g., rocm6.1) from installed tools or torch.
    Returns None if unknown. Best-effort only; torch will still run CPU if needed.
    """
    # Try torch in existing venv
    if venv.PYTHON.exists():
        try:
            code = "import torch, json; print(json.dumps({'hip': getattr(torch.version,'hip',None)}))"
            out = output([str(venv.PYTHON), "-c", code])
            if out:
                import json
                hip = json.loads(out).get("hip")
                if hip and isinstance(hip, str):
                    # Example: '6.1'
                    parts = hip.split(".")
                    if parts and parts[0].isdigit():
                        return f"rocm{parts[0]}.{parts[1] if len(parts)>1 else '0'}"
        except Exception:
            pass
    # Fallback: use rocminfo presence as hint (series unknown)
    if has_cmd("rocminfo"):
        # Assume latest ROCm series mapping; leave None to keep CPU nightly by default
        return None
    return None


def install_pytorch_nightly(rocm_preferred: bool = True) -> None:
    venv.ensure()
    series = _detect_rocm_series() if rocm_preferred else None
    if series:
        # Placeholder: real ROCm nightly wheels vary; manylinux wheels often under this index
        # If incompatible, pip will fail; caller can retry with CPU.
        idx = f"https://download.pytorch.org/whl/nightly/{series}"
        try:
            venv.pip_install(["--pre", "torch", "torchvision", "torchaudio", "--index-url", idx])
            return
        except Exception:
            # Retry CPU nightly fallback
            pass
    # CPU nightly fallback
    venv.pip_install(["--pre", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/nightly/cpu"])


def setup_rocm_and_pytorch_nightly():
    # Minimal: ensure deps and venv, leave ROCm driver to user (root-required)
    ensure_packages(["git", "python3-venv", "python3-pip", "build-essential", "cmake"])
    install_pytorch_nightly(rocm_preferred=True)


def run_setup_wizard(base_dir: Path | None = None, venv_name: str | None = None, install_comfy: bool = True) -> None:
    """Guided setup: configure base dir/venv, check WSL GPU, install base and ComfyUI."""
    from .config import save_config, get_base_dir, get_venv_name
    # Persist configuration if provided
    if base_dir or venv_name:
        save_config(base_dir=base_dir, venv_name=venv_name)

    # Pre-checks
    kfd = Path("/dev/kfd").exists()
    dri = Path("/dev/dri").exists()
    # Ensure essential packages and python env
    ensure_packages(["git", "python3-venv", "python3-pip", "build-essential", "cmake"])

    # Install PyTorch (ROCm-preferred)
    try:
        install_pytorch_nightly(rocm_preferred=True)
    except Exception:
        install_pytorch_nightly(rocm_preferred=False)

    if install_comfy:
        from ..tools.image import install_comfyui
        install_comfyui()

    # Print a short summary (stdout)
    summary = [
        f"Base dir: {get_base_dir()}",
        f"Venv: {get_venv_name()}",
        f"/dev/kfd: {'present' if kfd else 'missing'}",
        f"/dev/dri: {'present' if dri else 'missing'}",
    ]
    print("\n".join(summary))
