# Vector Vision

A lightweight **image search system** that supports:

* **Text-based search** (search images using text prompts)
* **Image-based search** (find similar images from an uploaded image)
* **Dataset upload** via ZIP (old dataset and index automatically replaced)
* Fast retrieval using **FAISS**
* Universal embeddings using **CLIP**
* Simple and clean **Streamlit frontend**

---

## Tech Stack

**Backend**

* FastAPI
* Sentence Transformers (CLIP – ViT-B/32)
* FAISS (vector search)
* Pillow

**Frontend**

* Streamlit
* Requests

---

## What This Project Does

* Upload a ZIP containing images → index is built automatically
* Search using **text** or **image**
* Displays results in a simple grid
* Shows the **query image** for image-search
* Keeps only the **latest query image** to avoid caching issues
