import json
import faiss
import os
import numpy as np
from utils.embeddings import EmbeddingModel

CHUNKS_PATH = "data/chunks.json"
INDEX_DIR = "data/faiss_index"

def build_faiss_index():
    # Load preprocessed chunks
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [chunk["content"] for chunk in chunks]

    # Generate embeddings
    model = EmbeddingModel()
    vectors = model.encode(texts)
    
    # Create FAISS index
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    # Save index
    os.makedirs(INDEX_DIR, exist_ok=True)
    faiss.write_index(index, os.path.join(INDEX_DIR, "rbi_index.faiss"))

    # Save metadata for mapping
    with open(os.path.join(INDEX_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    print(f"[✓] Stored {len(texts)} vectors in FAISS index at {INDEX_DIR}")

if __name__ == "__main__":
    build_faiss_index()
