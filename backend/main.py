import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
import zipfile
import shutil
import logging
from sentence_transformers import SentenceTransformer
from uuid import uuid4
import os

from config import DATASET_DIR, INDEX_PATH, ALLOWED_IMAGE_EXTS
from utils import rewrite_path, clear_dataset_and_index, allowed_image
from indexing import build_index, load_index
from retrieval import search_by_image, search_by_text

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Image Search Engine")

# Setup static files to serve images
DATASET_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/images", StaticFiles(directory=str(DATASET_DIR)), name="images")

# Load model at startup
@app.on_event("startup")
def startup():
    logger.info("Loading SentenceTransformer model (clip-ViT-B-32)...")
    app.state.model = SentenceTransformer("clip-ViT-B-32")
    app.state.index = None
    app.state.image_paths = None
    # attempt to load existing index if present
    try:
        if INDEX_PATH.exists():
            logger.info("Found existing index. Loading...")
            idx, paths = load_index(INDEX_PATH)
            app.state.index = idx
            app.state.image_paths = paths
            logger.info("Index loaded with %d images", len(paths))
    except Exception as e:
        logger.warning("Failed to load existing index: %s", e)

@app.post("/upload-folder/", summary="Upload a .zip dataset; existing dataset & index are deleted first")
async def upload_images_zip(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".zip"): # type: ignore
        raise HTTPException(status_code=400, detail="Only .zip files allowed.")

    # Delete old dataset + index
    logger.info("Clearing existing dataset and index...")
    clear_dataset_and_index()

    # Save zip temporarily
    temp_zip = Path("temp_upload.zip")
    with temp_zip.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract into dataset dir
    try:
        with zipfile.ZipFile(str(temp_zip), "r") as z:
            z.extractall(str(DATASET_DIR))
    finally:
        temp_zip.unlink(missing_ok=True)

    # Build index immediately (blocking). If dataset is huge, consider moving to background task.
    try:
        index, image_paths = build_index(DATASET_DIR, app.state.model, INDEX_PATH)
        app.state.index = index
        app.state.image_paths = image_paths
        return {"message": "Index created", "total_images": len(image_paths)}
    except Exception as exc:
        logger.exception("Index build failed")
        raise HTTPException(status_code=500, detail=f"Index build failed: {exc}")



@app.post("/search-image/", summary="Upload a query image; get query image URL + retrieved images")
async def api_search_image(file: UploadFile = File(...), top_k: int = Query(5, ge=1, le=100)):

    if not allowed_image(file.filename, ALLOWED_IMAGE_EXTS):
        raise HTTPException(status_code=400, detail="Invalid image format.")

    # Ensure index is loaded
    if app.state.index is None:
        try:
            idx, paths = load_index(INDEX_PATH)
            app.state.index = idx
            app.state.image_paths = paths
        except Exception:
            raise HTTPException(status_code=404, detail="No index found. Upload a dataset first.")

    # 🔥 Delete any existing query images
    for f in DATASET_DIR.glob("query_*.jpg"):
        try:
            f.unlink()
        except:
            pass

    # 🔥 Create a NEW unique filename every time
    unique_name = f"query_{uuid4().hex}.jpg"
    query_path = DATASET_DIR / unique_name

    # Save image
    with query_path.open("wb") as dest:
        shutil.copyfileobj(file.file, dest)

    # 🔍 Run retrieval
    results = search_by_image(str(query_path), app.state.model, app.state.index, app.state.image_paths, top_k)

    # Build URLs
    query_url = rewrite_path(str(query_path))
    result_urls = [rewrite_path(p) for p in results]

    return {"query_image": query_url, "results": result_urls}


@app.get("/search-text/", summary="Return images matching a text query")
async def api_search_text(query: str = Query(..., min_length=1), top_k: int = Query(5, ge=1, le=100)):
    if app.state.index is None:
        try:
            idx, paths = load_index(INDEX_PATH)
            app.state.index = idx
            app.state.image_paths = paths
        except Exception:
            raise HTTPException(status_code=404, detail="No index found. Upload a dataset first.")

    results = search_by_text(query, app.state.model, app.state.index, app.state.image_paths, top_k)
    urls = [rewrite_path(p) for p in results]
    return {"results": urls}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
