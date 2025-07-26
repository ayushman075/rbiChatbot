import json
import os
import pickle
import faiss

INDEX_DIR = "data/faiss_index"

def save_faiss_index_as_pkl():
    # Load FAISS index
    index_path = os.path.join(INDEX_DIR, "rbi_index.faiss")
    index = faiss.read_index(index_path)

    # Load metadata
    metadata_path = os.path.join(INDEX_DIR, "metadata.json")
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Save as pickle
    with open(os.path.join(INDEX_DIR, "faiss_index.pkl"), "wb") as f:
        pickle.dump({"index": index, "metadata": metadata}, f)

    print(f"[✓] Pickle file saved at {INDEX_DIR}/faiss_index.pkl")

if __name__ == "__main__":
    save_faiss_index_as_pkl()
