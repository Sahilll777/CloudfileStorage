# routes/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import mysql.connector
from config import MYSQL_CONFIG

auth_bp = Blueprint("auth", __name__)

# ---------------- Helper ----------------
def get_db_connection():
    """Create a new MySQL connection."""
    return mysql.connector.connect(**{k: v for k, v in MYSQL_CONFIG.items() if v is not None})

# ---------------- Signup ----------------
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    raw_password = data.get("password")

    if not username or not email or not raw_password:
        return jsonify({"error": "username, email, and password are required"}), 400

    hashed_password = generate_password_hash(raw_password)

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password),
        )
        conn.commit()
        return jsonify({"message": "User created successfully"}), 201

    except mysql.connector.IntegrityError:
        return jsonify({"error": "User with that email or username already exists"}), 400

    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---------------- Login ----------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if not check_password_hash(user["password"], password):
            return jsonify({"error": "Invalid email or password"}), 401

        # ✔ FIX: Convert identity to STRING
        token = create_access_token(identity=str(user["id"]))

        return jsonify({"token": token, "username": user["username"]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
