from flask import Blueprint, request, jsonify
from app.retriever import get_top_chunks
from utils.gemini_llm import generate_response as generate_answer
from utils.retriever import VectorRetriever
from flask_cors import CORS, cross_origin


retriever = VectorRetriever()



api = Blueprint("api", __name__)

@api.route("/", methods=["GET"])
@cross_origin(origins=['http://localhost:5173',"https://rbi-chatbot-frontend.vercel.app"]) 
def check_server():
    try:
        return jsonify({
            "res":"Got your request, yaar"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



@api.route("/query", methods=["POST"])
@cross_origin(origins=['http://localhost:5173',"https://rbi-chatbot-frontend.vercel.app"]) 
def query_rbi():
    data = request.get_json()
    question = data.get("question")
    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        top_chunks = retriever.retrieve(question)
        answer = generate_answer(question, top_chunks)
        print(answer)
        return jsonify({
            "answer": answer
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
