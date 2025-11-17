from pathlib import Path
import shutil
import os
from typing import Iterable
from config import DATASET_DIR, INDEX_PATH

def rewrite_path(abs_path: str) -> str:
    """
    Convert local filesystem path → API URL path exposed by StaticFiles.
    e.g. uploaded_images/cats/1.jpg -> /images/cats/1.jpg
    """
    try:
        p = Path(abs_path).resolve()
        rel = p.relative_to(Path(DATASET_DIR).resolve())
        return "/images/" + str(rel).replace("\\", "/")
    except Exception:
        return "/images/" + str(Path(abs_path).name)

def clear_dataset_and_index() -> None:
    """
    Delete dataset directory and index files.
    """
    # remove images
    if DATASET_DIR.exists():
        shutil.rmtree(DATASET_DIR)
    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    # remove index & paths file if exists
    if INDEX_PATH.exists():
        INDEX_PATH.unlink(missing_ok=True)
    if (INDEX_PATH.with_suffix(INDEX_PATH.suffix + ".paths")).exists():
        (INDEX_PATH.with_suffix(INDEX_PATH.suffix + ".paths")).unlink(missing_ok=True)

def allowed_image(filename: str, allowed_exts: Iterable[str]) -> bool:
    return Path(filename).suffix.lower() in allowed_exts
