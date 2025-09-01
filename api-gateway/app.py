# api-gateway/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# CORS allowlist (virgülle ayır)
origins = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "").split(",") if o.strip()]
if origins:
    CORS(app, origins=origins, supports_credentials=True)
else:
    CORS(app)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001").rstrip("/")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:5002").rstrip("/")

# ---- Port & Host (IPv6 uyumlu) ----
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "::")  # IPv6 (dual-stack)
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

def proxy_request(service_url: str, path: str):
    url = f"{service_url}/{path.lstrip('/')}"
    # Problemli header'ları çıkar
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in ("host", "content-length", "content-encoding", "connection")}

    try:
        method = request.method.upper()
        if method == "GET":
            resp = requests.get(url, headers=headers, params=request.args, timeout=30)
        elif method == "POST":
            # hem JSON hem form/body desteği
            json_body = request.get_json(silent=True)
            data_body = None if json_body is not None else request.get_data()
            resp = requests.post(url, headers=headers, json=json_body, data=data_body, timeout=30)
        elif method == "PUT":
            json_body = request.get_json(silent=True)
            data_body = None if json_body is not None else request.get_data()
            resp = requests.put(url, headers=headers, json=json_body, data=data_body, timeout=30)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=30)
        else:
            return jsonify({"error": "Method not allowed"}), 405

        # JSON değilse de makul döndür
        try:
            return resp.json(), resp.status_code
        except ValueError:
            return resp.text, resp.status_code
    except requests.exceptions.RequestException as e:
        return {"error": f"Service unavailable: {e}"}, 503

@app.route("/auth/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def auth_proxy(path):
    return proxy_request(AUTH_SERVICE_URL, path)

@app.route("/users/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def users_proxy(path):
    return proxy_request(USER_SERVICE_URL, path)

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "api-gateway",
        "environment": os.getenv("ENV", "production")
    }), 200

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
