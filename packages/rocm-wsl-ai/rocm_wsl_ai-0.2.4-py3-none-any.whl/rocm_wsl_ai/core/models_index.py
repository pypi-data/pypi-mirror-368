from __future__ import annotations
import json
import hashlib
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Iterable, List, Optional, Dict
from .models import get_store_root, get_image_root, get_llm_root, ensure_store
from .config import _config_path


SUPPORTED_EXTS = {
    # image
    ".safetensors", ".ckpt", ".pt", ".pth", ".onnx", ".vae",
    # llm
    ".gguf", ".ggml", ".bin",
}


@dataclass
class ModelEntry:
    path: str
    category: str  # e.g., image/checkpoints, image/vae, llm/gguf
    size: int
    mtime: float
    sha256: Optional[str] = None
    tags: List[str] = field(default_factory=list)


def _db_path() -> Path:
    return _config_path().parent / "models.json"


def _iter_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
            yield p


def _categorize(p: Path) -> str:
    try:
        rel = p.relative_to(get_store_root())
        parts = list(rel.parts)
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
    except Exception:
        pass
    # fallback
    if p.suffix.lower() in {".gguf", ".ggml", ".bin"}:
        return "llm/other"
    return "image/other"


def scan_store() -> Dict[str, ModelEntry]:
    ensure_store()
    root = get_store_root()
    entries: Dict[str, ModelEntry] = {}
    for f in _iter_files(root):
        try:
            st = f.stat()
            cat = _categorize(f)
            key = str(f.resolve())
            entries[key] = ModelEntry(
                path=key,
                category=cat,
                size=st.st_size,
                mtime=st.st_mtime,
                sha256=None,
                tags=[],
            )
        except Exception:
            continue
    return entries


def load_index() -> Dict[str, ModelEntry]:
    p = _db_path()
    if not p.exists():
        return {}
    try:
        raw = json.loads(p.read_text("utf-8"))
        out: Dict[str, ModelEntry] = {}
        for k, v in raw.items():
            out[k] = ModelEntry(**v)
        return out
    except Exception:
        return {}


def save_index(idx: Dict[str, ModelEntry]) -> None:
    p = _db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {k: asdict(v) for k, v in idx.items()}
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def refresh_index() -> Dict[str, ModelEntry]:
    idx = scan_store()
    save_index(idx)
    return idx


def compute_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def ensure_hashed(entry: ModelEntry) -> ModelEntry:
    if entry.sha256:
        return entry
    p = Path(entry.path)
    if p.exists():
        entry.sha256 = compute_sha256(p)
    return entry
