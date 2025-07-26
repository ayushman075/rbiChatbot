from utils.retriever import VectorRetriever
from utils.gemini_llm import generate_response

retriever = VectorRetriever()

def main():
    while True:
        query = input("\n🔍 Enter your query (or type 'exit'): ")
        if query.lower() == "exit":
            break
        top_chunks = retriever.retrieve(query)
        response = generate_response(query, top_chunks)
        print("\n🧠 RBI Chatbot Response:\n")
        print(response)

if __name__ == "__main__":
    main()
