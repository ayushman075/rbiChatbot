import pickle
from sentence_transformers import SentenceTransformer

class VectorRetriever:
    def __init__(self, pkl_path="data/faiss_index/faiss_index.pkl"):
        with open(pkl_path, "rb") as f:
            data = pickle.load(f)
        
        self.index = data["index"]
        self.metadata = data["metadata"]
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def retrieve(self, query, top_k=4):
        # Encode the query to vector
        query_vector = self.model.encode([query])
        
        # Search the index
        distances, indices = self.index.search(query_vector, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                results.append({
                    "content": self.metadata[idx]["content"],
                    "score": float(distances[0][i]),
                    "source": self.metadata[idx].get("source", "")
                })
        return results
