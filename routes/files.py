# routes/files.py
import os
import time
import io
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.s3_helper import upload_bytes, generate_presigned_url, delete_s3_object
from database import save_file_record, list_user_files, get_file_record, delete_file_record

files_bp = Blueprint("files", __name__)


# -------------------------------------------------------
# UPLOAD FILE
# -------------------------------------------------------
@files_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = file.filename

    # Read file safely in memory
    file_bytes = file.read()
    size = len(file_bytes)

    s3_key = f"user_{user_id}/{filename}"

    try:
        upload_bytes(file_bytes, s3_key)
    except Exception as e:
        return jsonify({"error": f"S3 upload failed: {str(e)}"}), 500

    uploaded_at = time.strftime("%d %b %Y %H:%M")

    save_file_record(user_id, filename, s3_key, size, uploaded_at)

    return jsonify({
        "message": "File uploaded successfully",
        "filename": filename,
        "file_size": size,
        "uploaded_at": uploaded_at,
        "s3_key": s3_key
    }), 200


# -------------------------------------------------------
# LIST FILES
# -------------------------------------------------------
@files_bp.route("/list", methods=["GET"])
@jwt_required()
def list_files():
    user_id = get_jwt_identity()
    files = list_user_files(user_id)
    return jsonify({"files": files}), 200


# -------------------------------------------------------
# DOWNLOAD — returns presigned URL
# -------------------------------------------------------
@files_bp.route("/download", methods=["GET"])
@jwt_required()
def download_file():
    s3_key = request.args.get("s3_key")
    if not s3_key:
        return jsonify({"error": "Missing s3_key"}), 400

    try:
        url = generate_presigned_url(s3_key)
        return jsonify({"presigned_url": url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------
# DELETE FILE
# -------------------------------------------------------
@files_bp.route("/delete", methods=["DELETE"])
@jwt_required()
def delete_file():
    s3_key = request.args.get("s3_key")
    if not s3_key:
        return jsonify({"error": "Missing s3_key"}), 400

    try:
        delete_s3_object(s3_key)
        delete_file_record(s3_key)

        return jsonify({"message": "File deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
