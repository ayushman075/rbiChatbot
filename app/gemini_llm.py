from utils.gemini_llm import GeminiWrapper

gemini = GeminiWrapper()

def generate_answer(query, chunks):
    context = "\n\n".join([chunk["content"] for chunk in chunks])
    return gemini.ask_with_context(query, context)
