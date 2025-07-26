from flask import Flask
from flask_cors import CORS
from app.routes import api
from flask_cors import CORS, cross_origin


def create_app():
    app = Flask(__name__)
    CORS(app, origins=['http://localhost:5173',"https://rbi-chatbot-frontend.vercel.app"])
    app.register_blueprint(api, url_prefix="/api")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
