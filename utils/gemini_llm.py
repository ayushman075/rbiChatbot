import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")

def generate_response(query: str, retrieved_chunks: list[dict]) -> str:
    context = "\n\n".join([chunk["content"] for chunk in retrieved_chunks])
    prompt = f"""You are an assistant trained on RBI documents.
Use the following RBI context to answer the query.
 If there is any relevant link available in the context of query please return it.

Context:
{context}

Query: {query}

If the answer is based on a specific document, mention the title and attach the URL if available. 
"""

    response = model.generate_content(prompt)
    return response.text
