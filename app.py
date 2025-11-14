# app.py
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
import threading
import webbrowser

# initialize app
app = Flask(__name__)
CORS(app, supports_credentials=True)

# JWT config
app.config["JWT_SECRET_KEY"] = "419652cc89f0a9a9b6f0f93d712fa7e8"  # rotate in prod
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
jwt = JWTManager(app)

# upload folder (server-side temp, not used for S3 but keep for compatibility)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# register blueprints
from routes.auth import auth_bp
from routes.files import files_bp  # ensure this is the blueprint name used in routes/files.py

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(files_bp, url_prefix="/files")

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "CloudFileStorage API running",
        "upload_folder": app.config["UPLOAD_FOLDER"]
    }), 200


def open_browser():
    # optional: open test page or health
    import time
    time.sleep(1)
    webbrowser.open_new("http://127.0.0.1:5000/health")


if __name__ == "__main__":
    print("🚀 CloudFileStorage API Started")
    print(f"📂 Upload folder: {app.config['UPLOAD_FOLDER']}")
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host="127.0.0.1", port=5000, debug=True)
