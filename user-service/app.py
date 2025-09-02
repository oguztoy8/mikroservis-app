from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "user_db")

PORT = int(os.getenv("PORT", "8002"))
HOST = os.getenv("HOST", "::")  # IPv6 (dual-stack)

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
users_collection = db.user_profiles

# ---- helpers ------------------------------------------------
def to_serializable(doc: dict) -> dict:
    """ObjectId ve datetime alanlarını JSON'a çevir."""
    if not doc:
        return doc
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    for fld in ("created_at", "updated_at"):
        val = doc.get(fld)
        if isinstance(val, datetime):
            doc[fld] = val.isoformat()
    return doc
# -------------------------------------------------------------

@app.route("/create", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    # Tip karmaşasını önlemek için ISO string yazıyoruz
    data["created_at"] = datetime.utcnow().isoformat()
    user_id = users_collection.insert_one(data).inserted_id
    return jsonify({"id": str(user_id), "message": "User created"}), 201

@app.route("/get/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return jsonify(to_serializable(user)), 200
        return jsonify({"error": "User not found"}), 404
    except Exception:
        return jsonify({"error": "Invalid user ID"}), 400

@app.route("/update/<user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        data = request.get_json() or {}
        data["updated_at"] = datetime.utcnow().isoformat()
        result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
        if result.modified_count:
            return jsonify({"message": "User updated"}), 200
        return jsonify({"error": "User not found"}), 404
    except Exception:
        return jsonify({"error": "Invalid user ID"}), 400

@app.route("/delete/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count:
            return jsonify({"message": "User deleted"}), 200
        return jsonify({"error": "User not found"}), 404
    except Exception:
        return jsonify({"error": "Invalid user ID"}), 400

@app.route("/list", methods=["GET"])
def list_users():
    users = [to_serializable(u) for u in users_collection.find()]
    return jsonify(users), 200

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "user-service",
        "environment": os.getenv("ENV", "production")
    }), 200

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
