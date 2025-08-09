from __future__ import annotations
import os
from pathlib import Path

try:  # Python 3.11+
    import tomllib as toml
except Exception:  # Python 3.10 fallback
    import tomli as toml  # type: ignore


_DEFAULT_VENV_NAME = "genai_env"


def _config_path() -> Path:
    # Follow XDG on Linux/WSL, fall back to ~/.config
    xdg_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_home:
        return Path(xdg_home) / "rocm-wsl-ai" / "config.toml"
    return Path.home() / ".config" / "rocm-wsl-ai" / "config.toml"


def _load_toml() -> dict:
    cfg_file = _config_path()
    if not cfg_file.exists():
        return {}
    try:
        with cfg_file.open("rb") as f:
            return toml.load(f) or {}
    except Exception:
        return {}


def get_base_dir() -> Path:
    # Install base directory for tools; default to HOME
    env = os.environ.get("ROCM_WSL_AI_BASE_DIR")
    if env:
        return Path(env).expanduser()
    data = _load_toml()
    base = data.get("paths", {}).get("base_dir") if isinstance(data, dict) else None
    return Path(base).expanduser() if base else Path.home()


def get_venv_name() -> str:
    env = os.environ.get("ROCM_WSL_AI_VENV_NAME")
    if env:
        return env
    data = _load_toml()
    vname = data.get("python", {}).get("venv_name") if isinstance(data, dict) else None
    return vname or _DEFAULT_VENV_NAME


def save_config(
    *,
    base_dir: Path | None = None,
    venv_name: str | None = None,
    hf_token: str | None = None,
    civitai_token: str | None = None,
    auto_link_models: bool | None = None,
) -> Path:
    """Persist configuration to ~/.config/rocm-wsl-ai/config.toml (creates dirs).

    Only provided keys are updated; others remain unchanged.
    """
    cfg_file = _config_path()
    cfg_file.parent.mkdir(parents=True, exist_ok=True)
    data = _load_toml()
    if not isinstance(data, dict):
        data = {}
    if base_dir is not None:
        data.setdefault("paths", {})["base_dir"] = str(base_dir)
    if venv_name is not None:
        data.setdefault("python", {})["venv_name"] = venv_name
    if hf_token is not None or civitai_token is not None:
        tokens = data.setdefault("tokens", {})
        if hf_token is not None:
            tokens["huggingface"] = hf_token
        if civitai_token is not None:
            tokens["civitai"] = civitai_token
    if auto_link_models is not None:
        data.setdefault("models", {})["auto_link"] = bool(auto_link_models)
    # Write TOML manually to avoid extra deps
    lines: list[str] = []
    if "paths" in data:
        lines.append("[paths]")
        for k, v in data["paths"].items():
            lines.append(f"{k} = \"{v}\"")
        lines.append("")
    if "python" in data:
        lines.append("[python]")
        for k, v in data["python"].items():
            lines.append(f"{k} = \"{v}\"")
        lines.append("")
    if "tokens" in data:
        lines.append("[tokens]")
        for k, v in data["tokens"].items():
            lines.append(f"{k} = \"{v}\"")
        lines.append("")
    if "models" in data:
        lines.append("[models]")
        for k, v in data["models"].items():
            if isinstance(v, bool):
                lines.append(f"{k} = {'true' if v else 'false'}")
            else:
                lines.append(f"{k} = \"{v}\"")
        lines.append("")
    cfg_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return cfg_file


def get_auto_link_models() -> bool:
    env = os.environ.get("ROCM_WSL_AI_AUTO_LINK_MODELS")
    if env is not None:
        return env.strip().lower() not in ("0", "false", "no")
    data = _load_toml()
    try:
        val = data.get("models", {}).get("auto_link")
        if isinstance(val, bool):
            return val
    except Exception:
        pass
    return True


def get_hf_token() -> str | None:
    env = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if env:
        return env
    data = _load_toml()
    try:
        tok = data.get("tokens", {}).get("huggingface")
        return tok
    except Exception:
        return None


def get_civitai_token() -> str | None:
    env = os.environ.get("CIVITAI_TOKEN")
    if env:
        return env
    data = _load_toml()
    try:
        tok = data.get("tokens", {}).get("civitai")
        return tok
    except Exception:
        return None
