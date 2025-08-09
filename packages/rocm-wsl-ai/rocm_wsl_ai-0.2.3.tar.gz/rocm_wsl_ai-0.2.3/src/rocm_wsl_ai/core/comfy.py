from __future__ import annotations
import json
from pathlib import Path
from typing import Dict
from .config import get_base_dir
from .utils import git_clone_or_pull


def comfy_root() -> Path:
    return get_base_dir() / "ComfyUI"


def custom_nodes_dir() -> Path:
    return comfy_root() / "custom_nodes"


def ensure_manager() -> None:
    root = custom_nodes_dir()
    repo = "https://github.com/ltdrdata/ComfyUI-Manager.git"
    git_clone_or_pull(repo, root / "ComfyUI-Manager")


NODE_REPOS: Dict[str, str] = {
    # Heuristische Zuordnung von Node-Klassen zu Repos (erweiterbar)
    # Häufige Utility-Pakete
    "Impact": "https://github.com/ltdrdata/ComfyUI-Impact-Pack.git",
    # Qwen-Image: GGUF Loader und CLIP/UNet GGUF
    "UnetLoaderGGUF": "https://github.com/city96/ComfyUI-llama-cpp.git",
    "CLIPLoaderGGUF": "https://github.com/city96/ComfyUI-llama-cpp.git",
}


def ensure_nodes_for_workflow(workflow_json: Path) -> list[tuple[str, str]]:
    """Installiere benötigte Custom-Nodes auf Basis der im Workflow verwendeten class_type.
    Gibt Liste (class_type, repo_url) zurück, die installiert/übersprungen wurden.
    """
    ensure_manager()
    installed: list[tuple[str, str]] = []
    try:
        data = json.loads(workflow_json.read_text(encoding="utf-8"))
    except Exception:
        return installed
    classes: set[str] = set()
    # ComfyUI Workflow Format: dict mit 'nodes' oder indexbasiertem dict
    if isinstance(data, dict) and "nodes" in data and isinstance(data["nodes"], list):
        for n in data["nodes"]:
            ct = n.get("type") or n.get("class_type")
            if isinstance(ct, str):
                classes.add(ct)
    else:
        for _, n in (data.items() if isinstance(data, dict) else []):
            if isinstance(n, dict):
                ct = n.get("class_type") or n.get("type")
                if isinstance(ct, str):
                    classes.add(ct)

    dest = custom_nodes_dir()
    for ct in sorted(classes):
        for key, repo in NODE_REPOS.items():
            if key.lower() in ct.lower():
                git_clone_or_pull(repo, dest / Path(repo).stem)
                installed.append((ct, repo))
                break
    return installed


def install_workflow_from_url(url: str, dest_name: str | None = None) -> Path:
    import urllib.request
    wf_dir = comfy_root() / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    name = dest_name or Path(url).name or "workflow.json"
    dest = wf_dir / name
    with urllib.request.urlopen(url) as r:  # noqa: S310 (trusted user-provided URL)
        dest.write_bytes(r.read())
    return dest
