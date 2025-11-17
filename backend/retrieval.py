from PIL import Image
import numpy as np
from typing import List

def search_by_image(image_path: str, model, index, image_paths: List[str], top_k: int = 5):
    img = Image.open(image_path).convert("RGB")
    vec = model.encode(img).astype("float32").reshape(1, -1)
    img.close()
    # search
    distances, indices = index.search(vec, top_k)
    # filter negative ids (when fewer items)
    ids = [int(i) for i in indices[0] if int(i) >= 0]
    return [image_paths[i] for i in ids]

def search_by_text(query: str, model, index, image_paths: List[str], top_k: int = 5):
    vec = model.encode(query).astype("float32").reshape(1, -1)
    distances, indices = index.search(vec, top_k)
    ids = [int(i) for i in indices[0] if int(i) >= 0]
    return [image_paths[i] for i in ids]
