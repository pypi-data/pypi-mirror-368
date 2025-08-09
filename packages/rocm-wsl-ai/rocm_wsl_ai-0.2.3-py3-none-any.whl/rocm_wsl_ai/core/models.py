from __future__ import annotations
import os
import shutil
from pathlib import Path
from typing import Iterable, Tuple
from .config import get_base_dir, save_config


# Shared model store layout under a single root
#   <base>/models/image/{checkpoints,vae,loras,embeddings,controlnet,clip,upscalers}
#   <base>/models/llm/{gguf,hf,other}


def get_store_root() -> Path:
    return get_base_dir() / "models"


def get_image_root() -> Path:
    return get_store_root() / "image"


def get_llm_root() -> Path:
    return get_store_root() / "llm"


def ensure_store() -> dict[str, Path]:
    """Create the shared model store directory structure and return paths."""
    image_sub = [
        "checkpoints",  # SD/SDXL checkpoints
        "vae",
        "loras",
        "embeddings",
        "controlnet",
        "clip",
        "upscalers",
    ]
    llm_sub = [
        "gguf",  # llama.cpp, koboldcpp
        "hf",    # text-gen-webui huggingface/transformers
        "other",
    ]
    paths: dict[str, Path] = {}
    for d in image_sub:
        p = get_image_root() / d
        p.mkdir(parents=True, exist_ok=True)
        paths[f"image/{d}"] = p
    for d in llm_sub:
        p = get_llm_root() / d
        p.mkdir(parents=True, exist_ok=True)
        paths[f"llm/{d}"] = p
    return paths


def _is_empty_dir(p: Path) -> bool:
    try:
        return p.is_dir() and not any(p.iterdir())
    except Exception:
        return False


def _safe_symlink_dir(target: Path, link_path: Path, adopt: bool = False) -> Tuple[bool, str]:
    """Create a directory symlink link_path -> target.
    - If link_path exists and is symlink, update if points elsewhere.
    - If link_path exists and is empty dir: remove and link.
    - If link_path exists and has content:
      * adopt=True: move all content into target, then replace with symlink.
      * adopt=False: skip with message.
    Returns (ok, message)
    """
    try:
        link_path.parent.mkdir(parents=True, exist_ok=True)
        target.mkdir(parents=True, exist_ok=True)
        if link_path.is_symlink():
            try:
                cur = link_path.readlink()
            except OSError:
                cur = None
            if cur and cur.resolve() == target.resolve():
                return True, "ok (already linked)"
            link_path.unlink()
        if link_path.exists():
            if _is_empty_dir(link_path):
                link_path.rmdir()
            else:
                if adopt:
                    # move contents into target
                    for item in list(link_path.iterdir()):
                        dest = target / item.name
                        if dest.exists():
                            # If conflict, keep existing in target; rename source
                            dest_conflict = target / f"_old_{item.name}"
                            shutil.move(str(item), str(dest_conflict))
                        else:
                            shutil.move(str(item), str(dest))
                    # remove original dir
                    try:
                        link_path.rmdir()
                    except Exception:
                        pass
                else:
                    return False, f"skip (non-empty: {link_path})"
        os.symlink(str(target), str(link_path), target_is_directory=True)
        return True, "linked"
    except Exception as e:
        return False, f"error: {e}"


def link_tool(tool: str, adopt: bool = False) -> list[tuple[Path, Path, bool, str]]:
    """Create symlinks for a given tool to the shared model store.
    Returns a list of (target, link_path, ok, message).
    """
    base = get_base_dir()
    image = ensure_store()  # ensures dirs
    results: list[tuple[Path, Path, bool, str]] = []

    def do(target: Path, link: Path):
        ok, msg = _safe_symlink_dir(target, link, adopt=adopt)
        results.append((target, link, ok, msg))

    t = tool.lower()
    if t in ("a1111", "automatic1111"):
        root = base / "stable-diffusion-webui" / "models"
        do(get_image_root() / "checkpoints", root / "Stable-diffusion")
        do(get_image_root() / "vae", root / "VAE")
        do(get_image_root() / "loras", root / "Lora")
        do(get_image_root() / "embeddings", base / "stable-diffusion-webui" / "embeddings")
        do(get_image_root() / "controlnet", root / "ControlNet")
        do(get_image_root() / "clip", root / "CLIP")
        # upscalers: projects differ; link both common locations
        do(get_image_root() / "upscalers", root / "ESRGAN")
        do(get_image_root() / "upscalers", root / "RealESRGAN")
        return results
    if t in ("forge",):
        root = base / "stable-diffusion-webui-forge" / "models"
        do(get_image_root() / "checkpoints", root / "Stable-diffusion")
        do(get_image_root() / "vae", root / "VAE")
        do(get_image_root() / "loras", root / "Lora")
        do(get_image_root() / "embeddings", base / "stable-diffusion-webui-forge" / "embeddings")
        do(get_image_root() / "controlnet", root / "ControlNet")
        do(get_image_root() / "clip", root / "CLIP")
        do(get_image_root() / "upscalers", root / "ESRGAN")
        do(get_image_root() / "upscalers", root / "RealESRGAN")
        return results
    if t in ("sdnext",):
        root = base / "SD.Next" / "models"
        do(get_image_root() / "checkpoints", root / "Stable-diffusion")
        do(get_image_root() / "vae", root / "VAE")
        do(get_image_root() / "loras", root / "Lora")
        do(get_image_root() / "embeddings", base / "SD.Next" / "embeddings")
        do(get_image_root() / "controlnet", root / "ControlNet")
        do(get_image_root() / "clip", root / "CLIP")
        do(get_image_root() / "upscalers", root / "ESRGAN")
        do(get_image_root() / "upscalers", root / "RealESRGAN")
        return results
    if t in ("comfyui",):
        root = base / "ComfyUI" / "models"
        do(get_image_root() / "checkpoints", root / "checkpoints")
        do(get_image_root() / "vae", root / "vae")
        do(get_image_root() / "loras", root / "loras")
        do(get_image_root() / "embeddings", root / "embeddings")
        do(get_image_root() / "controlnet", root / "controlnet")
        do(get_image_root() / "clip", root / "clip")
        do(get_image_root() / "upscalers", root / "upscale_models")
        return results
    if t in ("textgen", "text-generation-webui", "oobabooga"):
        root = base / "text-generation-webui"
        do(get_llm_root(), root / "models")
        return results
    if t in ("llama.cpp", "llama_cpp"):
        root = base / "llama.cpp"
        do(get_llm_root() / "gguf", root / "models")
        return results
    if t in ("koboldcpp",):
        root = base / "KoboldCpp"
        do(get_llm_root() / "gguf", root / "models")
        return results
    # Unknown tool: no-op
    return results


def link_all(adopt: bool = False) -> list[tuple[str, list[tuple[Path, Path, bool, str]]]]:
    tools = [
        "comfyui", "sdnext", "forge", "a1111",
        "textgen", "llama.cpp", "koboldcpp",
    ]
    results = []
    for t in tools:
        results.append((t, link_tool(t, adopt=adopt)))
    return results


def where() -> dict[str, Path]:
    ensure_store()
    return {
        "store": get_store_root(),
        "image": get_image_root(),
        "llm": get_llm_root(),
    }
