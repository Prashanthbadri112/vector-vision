import faiss
import numpy as np
from glob import glob
from pathlib import Path
from PIL import Image
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

def _find_image_files(images_dir: Path):
    exts = {".jpg", ".jpeg", ".png"}
    files = []
    for ext in exts:
        files.extend(glob(str(images_dir / f"**/*{ext}"), recursive=True))
    # include uppercase just in case
    files = sorted(files)
    return files

def generate_embeddings_from_paths(image_paths: List[str], model, batch_size: int = 16):
    """
    Encodes images in batches using SentenceTransformer model.encode(list_of_pil_images).
    Returns numpy array (n, dim)
    """
    embs = []
    batch = []
    paths_batch = []
    for p in image_paths:
        img = Image.open(p).convert("RGB")
        batch.append(img)
        paths_batch.append(p)
        if len(batch) >= batch_size:
            arr = model.encode(batch)  # list of vectors -> np.array
            embs.append(arr)
            # cleanup
            for im in batch:
                im.close()
            batch = []
            paths_batch = []

    if batch:
        arr = model.encode(batch)
        embs.append(arr)
        for im in batch:
            im.close()

    embeddings = np.vstack(embs).astype("float32")
    return embeddings

def build_index(images_dir: Path, model, index_path: Path) -> Tuple[faiss.Index, List[str]]:
    """
    Build FAISS index from images in images_dir using model.
    Also write index_path and index_path.paths file.
    """
    image_paths = _find_image_files(images_dir)
    if len(image_paths) == 0:
        raise RuntimeError("No images found in dataset directory.")

    logger.info(f"Found {len(image_paths)} images. Generating embeddings...")
    embeddings = generate_embeddings_from_paths(image_paths, model)

    dim = embeddings.shape[1]
    logger.info(f"Embeddings shape: {embeddings.shape}. Creating FAISS index dim={dim} ...")
    index = faiss.IndexFlatIP(dim)        # inner-product; ensure embeddings normalized if using cosine-like
    index = faiss.IndexIDMap(index)

    ids = np.arange(len(image_paths)).astype("int64")
    index.add_with_ids(embeddings, ids) # type: ignore

    faiss.write_index(index, str(index_path))

    # write paths
    with open(str(index_path) + ".paths", "w", encoding="utf-8") as f:
        for p in image_paths:
            f.write(p + "\n")

    logger.info("Index and paths saved.")
    return index, image_paths

def load_index(index_path: Path):
    if not index_path.exists():
        raise FileNotFoundError("Index file not found.")
    index = faiss.read_index(str(index_path))
    with open(str(index_path) + ".paths", "r", encoding="utf-8") as f:
        paths = [line.strip() for line in f if line.strip()]
    return index, paths
