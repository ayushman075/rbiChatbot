from utils.retriever import VectorRetriever

retrieve_relevant_chunks = VectorRetriever()

def get_top_chunks(query, k=4):
    chunks = retrieve_relevant_chunks.retrieve(query)
    return chunks
