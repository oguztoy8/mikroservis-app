from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import hashlib
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "auth_db")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret-key-123")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "1"))

# ---- Port & Host (IPv6 uyumlu) ----
PORT = int(os.getenv("PORT", "8001"))
HOST = os.getenv("HOST", "::")  # IPv6 (dual-stack)

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
users_collection = db.users

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if users_collection.find_one({"username": username}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    })
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = users_collection.find_one({"username": username, "password": hashed_password})
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode(
        {"username": username, "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)},
        SECRET_KEY,
        algorithm="HS256",
    )
    # PyJWT 2.x string döndürür
    return jsonify({"token": token, "username": username}), 200

@app.route("/verify", methods=["POST"])
def verify():
    token = (request.get_json() or {}).get("token")
    if not token:
        return jsonify({"valid": False, "error": "Token required"}), 400
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({"valid": True, "username": decoded["username"]}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token expired"}), 401
    except Exception:
        return jsonify({"valid": False, "error": "Invalid token"}), 401

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "auth-service",
        "environment": os.getenv("ENV", "production")
    }), 200

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
