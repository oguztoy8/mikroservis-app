# api-gateway/app.py - Düzeltilmiş versiyon
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:5002')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

def proxy_request(service_url, path):
    """Improved proxy function"""
    url = f"{service_url}/{path}"
    
    # Filter out problematic headers
    headers = {key: value for key, value in request.headers.items() 
              if key.lower() not in ['host', 'content-length', 'content-encoding']}
    
    try:
        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.args, timeout=30)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=request.get_json(), timeout=30)
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request.get_json(), timeout=30)
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            return jsonify({"error": "Method not allowed"}), 405

        # Handle response
        try:
            return response.json(), response.status_code
        except ValueError:
            return {"message": "Success"}, response.status_code
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Service unavailable: {str(e)}"}, 503

@app.route('/auth/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def auth_proxy(path):
    return proxy_request(AUTH_SERVICE_URL, path)

@app.route('/users/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_proxy(path):
    return proxy_request(USER_SERVICE_URL, path)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "api-gateway",
        "environment": os.getenv('ENV', 'production')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)