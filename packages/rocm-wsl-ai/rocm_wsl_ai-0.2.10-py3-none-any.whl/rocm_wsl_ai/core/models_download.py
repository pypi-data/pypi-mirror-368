from __future__ import annotations
import json
import subprocess
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, Iterable, List, Tuple, Dict, Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from .models import ensure_store, get_image_root, get_llm_root
from .comfy import install_workflow_from_url, ensure_nodes_for_workflow
from .models_index import compute_sha256
from .config import get_hf_token, get_civitai_token


class DownloadError(Exception):
    pass


def _which(*candidates: str) -> Optional[str]:
    for c in candidates:
        if shutil.which(c):
            return c
    return None


def _headers_for_url(url: str) -> list[tuple[str, str]]:
    """Build auth headers based on URL host."""
    hf_token = get_hf_token()
    civitai_token = get_civitai_token()
    header_kv: list[tuple[str, str]] = []
    u = url.lower()
    if "huggingface.co" in u and hf_token:
        header_kv.append(("Authorization", f"Bearer {hf_token}"))
    if "civitai.com" in u and civitai_token:
        header_kv.append(("Authorization", f"Bearer {civitai_token}"))
    return header_kv


def download_file(url: str, dest: Path, checksum: str | None = None, retries: int = 5) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tool = _which("aria2c", "curl", "wget")
    if tool is None:
        raise DownloadError("No downloader found (install aria2c or curl or wget)")
    header_kv = _headers_for_url(url)
    # Flatten for tools
    aria_headers: list[str] = []
    curl_headers: list[str] = []
    wget_headers: list[str] = []
    for k, v in header_kv:
        aria_headers += ["--header", f"{k}: {v}"]
        curl_headers += ["-H", f"{k}: {v}"]
        wget_headers += ["--header", f"{k}: {v}"]
    for attempt in range(1, retries + 1):
        cmd: list[str]
        if tool == "aria2c":
            # parallel segments, resume, retries
            cmd = [
                "aria2c",
                "-x16", "-s16",
                "--continue=true",
                "--max-tries=5",
                "-o", dest.name,
                "-d", str(dest.parent),
                *aria_headers,
                url,
            ]
        elif tool == "curl":
            cmd = [
                "curl", "-L", "--retry", "5", "--retry-delay", "2",
                "-C", "-", "-o", str(dest),
                *curl_headers,
                url,
            ]
        else:
            cmd = [
                "wget", "-c", "--tries=5", "-O", str(dest),
                *wget_headers,
                url,
            ]
        rc = subprocess.call(cmd)
        if rc == 0:
            break
        if attempt == retries:
            raise DownloadError(f"download failed after {retries} tries: {url}")
    if checksum:
        if compute_sha256(dest) != checksum:
            raise DownloadError("checksum mismatch")
    return dest


def _http_json(url: str, headers: list[tuple[str, str]] | None = None, method: str = "GET") -> dict:
    req = Request(url, method=method)
    for k, v in (headers or []):
        req.add_header(k, v)
    try:
        with urlopen(req) as r:  # noqa: S310
            return json.loads(r.read().decode("utf-8"))
    except HTTPError as e:
        if e.code == 429:
            raise DownloadError("Civitai API rate limited (429). Bitte später erneut versuchen.")
        raise DownloadError(f"HTTP error {e.code} for {url}")
    except URLError as e:
        raise DownloadError(f"Network error for {url}: {e.reason}")


def get_content_length(url: str) -> int | None:
    """Return Content-Length for a URL if provided by server."""
    req = Request(url, method="HEAD")
    for k, v in _headers_for_url(url):
        req.add_header(k, v)
    try:
        with urlopen(req) as r:  # noqa: S310
            cl = r.headers.get("Content-Length")
            return int(cl) if cl and cl.isdigit() else None
    except Exception:
        return None


def _resolve_civitai_url_by_hash(hash_hex: str) -> str | None:
    api = f"https://civitai.com/api/v1/model-versions/by-hash/{hash_hex}"
    data = _http_json(api, headers=_headers_for_url(api))
    files = data.get("files") or []
    for f in files:
        if isinstance(f, dict) and f.get("downloadUrl"):
            return f["downloadUrl"]
    return None


def _resolve_civitai_url_by_model(model_id: int, filename: str | None = None) -> str | None:
    api = f"https://civitai.com/api/v1/models/{model_id}"
    data = _http_json(api, headers=_headers_for_url(api))
    vers = data.get("modelVersions") or []
    for v in vers:
        for f in (v.get("files") or []):
            dl = f.get("downloadUrl")
            if not dl:
                continue
            if not filename or f.get("name") == filename:
                return dl
    return None


def resolve_preset_url(preset: str) -> str:
    """Return a final URL for a preset (handles Civitai fields)."""
    spec = PRESETS[preset]
    # Direct URL wins
    if spec.get("url"):
        return spec["url"]
    # Civitai flows
    if "civitai_hash" in spec:
        url = _resolve_civitai_url_by_hash(spec["civitai_hash"])  # type: ignore[index]
        if url:
            return url
    if "civitai_model_id" in spec:
        url = _resolve_civitai_url_by_model(int(spec["civitai_model_id"]), spec.get("filename"))  # type: ignore[arg-type]
        if url:
            return url
    raise DownloadError(f"Kein URL für Preset '{preset}' ermittelbar")


def get_civitai_model(model_id: int) -> Dict[str, Any]:
    api = f"https://civitai.com/api/v1/models/{model_id}"
    return _http_json(api, headers=_headers_for_url(api))


def list_civitai_files_for_model(model_id: int) -> List[Dict[str, Any]]:
    """Return a flat list of files with version context: [{versionName, fileName, sizeBytes, downloadUrl}]"""
    data = get_civitai_model(model_id)
    out: List[Dict[str, Any]] = []
    for v in data.get("modelVersions", []) or []:
        vname = v.get("name") or "version"
        for f in v.get("files", []) or []:
            dl = f.get("downloadUrl")
            if not dl:
                continue
            out.append({
                "versionName": vname,
                "fileName": f.get("name") or "file",
                "sizeBytes": f.get("sizeKB", 0) * 1024 if isinstance(f.get("sizeKB"), (int, float)) else None,
                "downloadUrl": dl,
            })
    return out


# Simple curated presets
PRESETS = {
    # Image models
    "sdxl_base": {
        "category": "image/checkpoints",
        "filename": "sd_xl_base_1.0.safetensors",
        "url": "https://example.invalid/models/sd_xl_base_1.0.safetensors",
        "sha256": None,
    },
    "sdxl_vae": {
        "category": "image/vae",
        "filename": "sdxl_vae.safetensors",
        "url": "https://example.invalid/models/sdxl_vae.safetensors",
        "sha256": None,
    },
    # Qwen-Image (GGUF) – Größenangaben zur Orientierung
    # Quelle: https://huggingface.co/city96/Qwen-Image-gguf/tree/main
    "qwen_image_1.8b_q4_k_m": {
        "category": "image/checkpoints",
        "filename": "Qwen-Image-1.8B.Q4_K_M.gguf",
        "url": "https://huggingface.co/city96/Qwen-Image-gguf/resolve/main/Qwen-Image-1.8B.Q4_K_M.gguf?download=true",
        "size": "~1.2 GB",
        "sha256": None,
    },
    "qwen_image_4b_q4_k_m": {
        "category": "image/checkpoints",
        "filename": "Qwen-Image-4B.Q4_K_M.gguf",
        "url": "https://huggingface.co/city96/Qwen-Image-gguf/resolve/main/Qwen-Image-4B.Q4_K_M.gguf?download=true",
        "size": "~2.5 GB",
        "sha256": None,
    },
    "qwen_image_7b_q4_k_m": {
        "category": "image/checkpoints",
        "filename": "Qwen-Image-7B.Q4_K_M.gguf",
        "url": "https://huggingface.co/city96/Qwen-Image-gguf/resolve/main/Qwen-Image-7B.Q4_K_M.gguf?download=true",
        "size": "~4.0 GB",
        "sha256": None,
    },
    # Qwen3 (Text LLM, mehrere Varianten als Beispiele)
    # Hinweis: URLs/Dateinamen variieren je nach Repo/Quant; bitte bei Bedarf anpassen.
    "qwen3_0.5b_q4_k_m": {
        "category": "llm/gguf",
        "filename": "Qwen3-0.5B.Q4_K_M.gguf",
        "url": "https://huggingface.co/ggml-org/Qwen3-GGUF/resolve/main/Qwen3-0.5B-Q4_K_M.gguf?download=true",
        "size": "~0.4 GB",
        "sha256": None,
    },
    "qwen3_1.8b_q4_k_m": {
        "category": "llm/gguf",
        "filename": "Qwen3-1.8B.Q4_K_M.gguf",
        "url": "https://huggingface.co/ggml-org/Qwen3-GGUF/resolve/main/Qwen3-1.8B-Q4_K_M.gguf?download=true",
        "size": "~1.2 GB",
        "sha256": None,
    },
    "qwen3_7b_q4_k_m": {
        "category": "llm/gguf",
        "filename": "Qwen3-7B.Q4_K_M.gguf",
        "url": "https://huggingface.co/ggml-org/Qwen3-GGUF/resolve/main/Qwen3-7B-Q4_K_M.gguf?download=true",
        "size": "~4.0 GB",
        "sha256": None,
    },
    "qwen3_14b_q4_k_m": {
        "category": "llm/gguf",
        "filename": "Qwen3-14B.Q4_K_M.gguf",
        "url": "https://huggingface.co/ggml-org/Qwen3-GGUF/resolve/main/Qwen3-14B-Q4_K_M.gguf?download=true",
        "size": "~8.0 GB",
        "sha256": None,
    },
}


def preset_path(preset: str) -> Path:
    spec = PRESETS[preset]
    base = get_image_root() if spec["category"].startswith("image/") else get_llm_root()
    return (base / spec["category"].split("/", 1)[1]) / spec["filename"]


def install_preset(preset: str, *, override_url: str | None = None, override_filename: str | None = None) -> Path:
    ensure_store()
    spec = PRESETS[preset]
    # Zielpfad ggf. mit Filename-Override
    if override_filename:
        base = get_image_root() if spec["category"].startswith("image/") else get_llm_root()
        dest = (base / spec["category"].split("/", 1)[1]) / override_filename
    else:
        dest = preset_path(preset)
    url = override_url or resolve_preset_url(preset)
    path = download_file(url, dest, checksum=spec.get("sha256"))
    # Compute SHA if not given and store alongside file (.sha256)
    if spec.get("sha256") is None and path.exists():
        sha = compute_sha256(path)
        (path.with_suffix(path.suffix + ".sha256")).write_text(sha, encoding="utf-8")
    # Post-hooks für bestimmte Presets
    if preset.startswith("qwen_image_"):
        # Installiere ComfyUI Workflow + benötigte Nodes (vom HF Repo media/)
        wf_url = "https://huggingface.co/city96/Qwen-Image-gguf/resolve/main/media/ComfyUI_Qwen_Image_Workflow.json?download=true"
        wf = install_workflow_from_url(wf_url, dest_name="Qwen-Image.json")
        ensure_nodes_for_workflow(wf)
    return path


def install_presets(presets: List[str], parallel: int = 3) -> list[Path]:
    """Install multiple presets in parallel. Returns list of downloaded paths."""
    ensure_store()
    results: list[Path] = []
    with ThreadPoolExecutor(max_workers=max(1, parallel)) as ex:
        futs = {ex.submit(install_preset, p): p for p in presets}
        for fut in as_completed(futs):
            results.append(fut.result())
    return results
