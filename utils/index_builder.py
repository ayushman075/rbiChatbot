import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class IndexUpdater:
    def __init__(self, index_path="data/faiss_index/rbi_index.faiss", metadata_path="data/faiss_index/metadata.json", model_name="all-MiniLM-L6-v2"):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.model = SentenceTransformer(model_name)

        # Load or initialize FAISS index
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        else:
            self.index = faiss.IndexFlatL2(384)  # 384 for MiniLM

        # Load metadata
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = []

    def add_documents(self, documents: list[dict]):
        texts = [doc["content"] for doc in documents]
        vectors = self.model.encode(texts)
        self.index.add(np.array(vectors))

        # Extend metadata
        self.metadata.extend(documents)

        # Save
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
