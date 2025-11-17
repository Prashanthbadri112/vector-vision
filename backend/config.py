from pathlib import Path

BASE_DIR = Path(__file__).parent
DATASET_DIR = BASE_DIR / "uploaded_images"
INDEX_PATH = BASE_DIR / "vector.index"
ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
