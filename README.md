# Vector Vision - An Image Search Engine

### Text & Image Based Retrieval using CLIP + FAISS + FastAPI + Streamlit

A fast and simple **image search engine** that supports:

* **Text-based search** → “cat”, “mountain”, “person wearing red jacket”, etc
* **Image-based search** → find visually similar images
* **Dataset upload** via ZIP → automatically rebuilds index
* **Clean Streamlit UI**
* **FAISS vector search** for extremely fast retrieval
* **CLIP embeddings (Sentence-Transformers)** for universal visual+text features

Supports **real-time query image display**, adjustable **Top-K results**, and automatic cleanup of old query images.

---

# Features

###  Upload & Rebuild Index

* Upload a `.zip` file containing images
* Old dataset **automatically deleted**
* New FAISS index built immediately
* Supports nested folders

---

###  Search by Text

Type any natural language query:

```
“dog running in grass”
“red car”
“snow mountains”
```

Returns the top-K most similar images using CLIP text embeddings.

---

###  Search by Image

Upload an image → backend computes visual embeddings and retrieves **most similar images**.

Also shows:

* The **query image**
* Retrieved result images in a grid
* Controls to adjust **K** value

---

###  Streamlit Frontend

A clean UI built with Streamlit:

* Dataset upload
* Text search
* Image search
* Adjustable `top_k` slider
* Beautiful responsive image grid layout

---

###  Backend API (FastAPI)

* `/upload-folder/` → Upload dataset zip
* `/search-text/` → Retrieve images from text query
* `/search-image/` → Retrieve images from image query
* Serving images via `/images/...`

---

# Tech Stack

| Component        | Technology                     |
| ---------------- | ------------------------------ |
| Embeddings       | CLIP (Sentence-Transformers)   |
| Vector Search    | FAISS (Inner Product / Cosine) |
| Backend API      | FastAPI                        |
| Frontend UI      | Streamlit                      |
| Image Processing | Pillow                         |
| Data Storage     | Local files                    |
| Deployment       | Uvicorn                        |

---

# Project Structure

```
image-search-engine/
│
├── backend/
│   ├── main.py
│   ├── indexing.py
│   ├── retrieval.py
│   ├── utils.py
│   ├── config.py
│   └── uploaded_images/        # auto-generated
│
└── frontend_streamlit/
    └── app.py
```

---

# Installation & Setup

## 1. Clone the repo

```bash
git clone https://github.com/yourusername/image-search-engine.git
cd image-search-engine
```

---

# Backend Setup (FastAPI)

## 1️Create virtual environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
```

## 2️Install dependencies

```bash
pip install -U pip
pip install fastapi uvicorn sentence-transformers faiss-cpu pillow
```

## 3️Run backend server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at:

```
http://localhost:8000
```

Images served at:

```
http://localhost:8000/images/...
```

---

# Frontend Setup (Streamlit)

Open a new terminal:

```bash
cd frontend_streamlit
pip install streamlit requests pillow
```

Run the Streamlit app:

```bash
streamlit run app.py
```

UI available at:

```
http://localhost:8501
```

---

# Usage Guide

## Upload Dataset

1. Go to the **Upload Dataset** tab
2. Upload `images.zip`
3. Index rebuilds automatically

Old dataset + index are deleted when new one is uploaded.

---

## Search by Text

1. Enter a query
2. Move slider to choose **Top-K**
3. Click **Search Text**
4. See results in a responsive grid

---

## Search by Image

1. Upload an image
2. Adjust **Top-K**
3. Click **Search by Image**
4. Query image shows up
5. Retrieved images appear in grid

Previous query image is automatically deleted from the server.

---

# Automatic Query Image Cleanup

Each time a new query image is uploaded:

* Old query image is deleted
* New image saved as `query_<uuid>.jpg`
* Prevents caching issues
* Always shows the latest query image





