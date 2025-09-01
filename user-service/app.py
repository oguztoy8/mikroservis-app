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

# ---- Port & Host (IPv6 uyumlu) ----
PORT = int(os.getenv("PORT", "8002"))
HOST = os.getenv("HOST", "::")  # IPv6 (dual-stack)

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
users_collection = db.user_profiles

@app.route("/create", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    data["created_at"] = datetime.utcnow()
    user_id = users_collection.insert_one(data).inserted_id
    return jsonify({"id": str(user_id), "message": "User created"}), 201

@app.route("/get/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
            if "created_at" in user:
                user["created_at"] = user["created_at"].isoformat()
            return jsonify(user), 200
        return jsonify({"error": "User not found"}), 404
    except Exception:
        return jsonify({"error": "Invalid user ID"}), 400

@app.route("/update/<user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        data = request.get_json() or {}
        data["updated_at"] = datetime.utcnow()
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
    users = []
    for user in users_collection.find():
        user["_id"] = str(user["_id"])
        if "created_at" in user:
            user["created_at"] = user["created_at"].isoformat()
        if "updated_at" in user:
            user["updated_at"] = user["updated_at"].isoformat()
        users.append(user)
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
