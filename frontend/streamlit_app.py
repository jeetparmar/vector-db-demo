import streamlit as st
import requests
import pandas as pd
import os
import json
from datetime import datetime

# Set page config
st.set_page_config(page_title="Vector DB Demo", page_icon="🚀", layout="wide")

# API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("🚀 Vector Database Demonstration")
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    db_type = st.selectbox(
        "Select Vector Database",
        ["ChromaDB", "Qdrant"],
        index=0
    ).lower()
    
    if db_type == "chromadb":
        db_type = "chroma"
    
    embedding_model = st.selectbox(
        "Embedding Model",
        [
            "sentence-transformers/all-MiniLM-L6-v2",
            "BAAI/bge-small-en-v1.5",
            "text-embedding-3-small (OpenAI)"
        ],
        index=0
    )
    
    collection_name = st.text_input("Collection Name", value="demo_collection")
    
    st.markdown("---")
    st.info("This app demonstrates how text is converted to vectors and stored in a vector database for similarity search.")

# Main Tabs
tabs = st.tabs(["📤 Upload & Process", "🔍 Similarity Search", "📊 Vector Operations", "📚 Documentation"])

# 1. Upload & Process Tab
with tabs[0]:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Choose a file (PDF, TXT, DOCX, MD)", type=["pdf", "txt", "docx", "md"])
    
    col1, col2 = st.columns(2)
    with col1:
        chunk_size = st.slider("Chunk Size (characters)", 100, 2000, 500)
    with col2:
        chunk_overlap = st.slider("Chunk Overlap (characters)", 0, 500, 100)
    
    if st.button("🚀 Process & Store"):
        if uploaded_file is not None:
            with st.spinner("Processing document..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                data = {
                    "db_type": db_type,
                    "embedding_model": embedding_model,
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "collection_name": collection_name
                }
                
                try:
                    response = requests.post(f"{API_URL}/process-document", files=files, data=data)
                    if response.status_code == 200:
                        res = response.json()
                        st.success(f"Successfully processed {res['document_name']}!")
                        
                        col_r1, col_r2, col_r3 = st.columns(3)
                        col_r1.metric("Chunks Created", res["chunks_created"])
                        col_r2.metric("DB Type", res["db_type"].upper())
                        col_r3.metric("Processing Time", res["processing_time"])
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")
        else:
            st.warning("Please upload a file first.")

# 2. Similarity Search Tab
with tabs[1]:
    st.header("Search Vectors")
    query = st.text_input("Enter search query")
    top_k = st.slider("Top K results", 1, 10, 3)
    
    if st.button("🔍 Search"):
        if query:
            with st.spinner("Searching..."):
                params = {
                    "query": query,
                    "db_type": db_type,
                    "embedding_model": embedding_model,
                    "collection_name": collection_name,
                    "top_k": top_k
                }
                try:
                    response = requests.get(f"{API_URL}/search", params=params)
                    if response.status_code == 200:
                        results = response.json()
                        if not results:
                            st.info("No results found.")
                        else:
                            for idx, r in enumerate(results):
                                with st.expander(f"Result {idx+1} (Score: {r['score']:.4f})"):
                                    st.write(f"**Source:** {r['metadata'].get('source', 'Unknown')}")
                                    st.write(f"**Content Snippet:**")
                                    st.info(r['document'])
                                    st.json(r['metadata'])
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")
        else:
            st.warning("Please enter a query.")

# 3. Vector Operations Tab
with tabs[2]:
    st.header("Collection Exploration")
    
    if st.button("🔄 Refresh Data"):
        st.rerun()

    try:
        response = requests.get(f"{API_URL}/collection-data", params={"db_type": db_type, "collection_name": collection_name})
        if response.status_code == 200:
            data = response.json()
            ids = data.get("ids", [])
            metadatas = data.get("metadatas", [])
            documents = data.get("documents", [])
            
            if not ids:
                st.info("Collection is empty or does not exist.")
            else:
                st.write(f"Showing {len(ids)} chunks in collection `{collection_name}` using `{db_type}`")
                
                # Display Summary Table
                df_data = []
                for i in range(len(ids)):
                    df_data.append({
                        "ID": ids[i],
                        "Source": metadatas[i].get("source", "N/A"),
                        "Chunk Index": metadatas[i].get("chunk_index", "N/A"),
                        "Content Preview": (documents[i][:100] + "...") if documents[i] else "N/A"
                    })
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
                
                # Advanced Options
                with st.expander("🛠️ Advanced Operations"):
                    doc_names = list(set([m.get("source") for m in metadatas if m.get("source")]))
                    selected_doc = st.selectbox("Select Document to Delete", doc_names)
                    if st.button("🗑️ Delete Document"):
                        del_res = requests.delete(f"{API_URL}/document", params={"db_type": db_type, "collection_name": collection_name, "doc_name": selected_doc})
                        if del_res.status_code == 200:
                            st.success(f"Deleted {selected_doc}")
                            st.rerun()
                    
                    if st.button("🔥 Clear Entire Collection", type="primary"):
                        clear_res = requests.delete(f"{API_URL}/collection", params={"db_type": db_type, "collection_name": collection_name})
                        if clear_res.status_code == 200:
                            st.success("Collection cleared.")
                            st.rerun()
        else:
            st.error("Could not fetch collection data.")
    except Exception as e:
        st.error(f"Connection failed: {e}")

# 4. Documentation Tab
with tabs[3]:
    st.header("Educational Guide")
    st.markdown("""
    ### What is a Vector Database?
    
    A **Vector Database** is a specialized database designed to store and query high-dimensional vectors. These vectors are mathematical representations of data like text, images, or audio.
    
    ### How it Works:
    1. **Embeddings**: Text is converted into numerical vectors (lists of numbers) using deep learning models (like BERT or OpenAI Ada).
    2. **Chunks**: Since documents can be long, we split them into smaller 'chunks' to ensure specific sections can be found.
    3. **Similarity Search**: Instead of looking for exact word matches, we calculate the 'distance' between vectors using algorithms like **Cosine Similarity**.
    
    ### Key Concepts:
    - **Vector**: A coordinate in high-dimensional space.
    - **Metadata**: Extra information (like filename or page number) stored alongside the vector.
    - **Top K**: The number of closest matches to return for a query.
    
    ### Why use ChromaDB vs Qdrant?
    - **ChromaDB**: Great for local development, easy to set up, and perfect for research.
    - **Qdrant**: High performance, production-ready, supports complex filtering and distributed setups.
    """)
