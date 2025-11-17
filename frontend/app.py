import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Image Search Engine", layout="wide")

st.title("🔍 Image Search Engine (Streamlit Frontend)")


# Utility to display image grid
def image_grid(urls, columns=4):
    if not urls:
        return
    rows = [urls[i:i + columns] for i in range(0, len(urls), columns)]
    for row in rows:
        cols = st.columns(len(row))
        for col, url in zip(cols, row):
            col.image(url, width='stretch')


# =============================
#      TAB NAVIGATION
# =============================
tab_upload, tab_text, tab_image = st.tabs(
    ["📁 Upload Dataset", "🔤 Text Search", "🖼️ Image Search"]
)


# =============================
#       UPLOAD DATASET TAB
# =============================
with tab_upload:
    st.subheader("Upload a ZIP dataset")
    file = st.file_uploader("Choose a .zip file of images", type=["zip"])

    if st.button("Upload & Rebuild Index"):
        if file is None:
            st.error("Please upload a .zip file.")
        else:
            with st.spinner("Uploading + rebuilding index..."):
                files = {"file": (file.name, file.getvalue(), "application/zip")}
                res = requests.post(f"{API_BASE}/upload-folder/", files=files)

            if res.status_code == 200:
                data = res.json()
                st.success(f"Index created successfully! Total images: {data['total_images']}")
            else:
                st.error(f"Error: {res.text}")


# =============================
#       TEXT SEARCH TAB
# =============================
with tab_text:
    st.subheader("Search images using text")

    query = st.text_input("Enter a text query")

    # 🔥 Slider for K-value
    top_k_text = st.slider("Number of results (Top-K)", 1, 30, 8)

    if st.button("Search Text"):
        if not query:
            st.error("Please enter a text query.")
        else:
            with st.spinner("Searching..."):
                res = requests.get(
                    f"{API_BASE}/search-text/",
                    params={"query": query, "top_k": top_k_text},
                )

            if res.status_code == 200:
                data = res.json()
                urls = [API_BASE + url for url in data["results"]]
                st.success(f"Found {len(urls)} images")

                image_grid(urls)
            else:
                st.error(f"Error: {res.text}")


# =============================
#       IMAGE SEARCH TAB
# =============================
with tab_image:
    st.subheader("Search using an image")

    img_file = st.file_uploader("Upload a query image:", type=["png", "jpg", "jpeg"])

    # 🔥 Slider for K-value
    top_k_img = st.slider("Number of results (Top-K)", 1, 30, 8, key="img_top_k")

    if st.button("Search by Image"):
        if img_file is None:
            st.error("Please upload an image.")
        else:
            with st.spinner("Searching..."):
                files = {"file": (img_file.name, img_file.getvalue(), img_file.type)}
                res = requests.post(
                    f"{API_BASE}/search-image/?top_k={top_k_img}",
                    files=files,
                )

            if res.status_code == 200:
                data = res.json()

                # The backend gives the query image URL + result image URLs
                query_url = API_BASE + data["query_image"]
                result_urls = [API_BASE + url for url in data["results"]]

                st.success("Query Image")
                st.image(query_url, width='stretch')

                st.subheader("Retrieved Images")
                image_grid(result_urls)
            else:
                st.error(f"Error: {res.text}")
