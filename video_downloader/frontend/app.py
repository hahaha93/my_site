from flask import Flask, render_template, request, jsonify, Response
import requests
import os

app = Flask(__name__)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8001")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def proxy_download():
    try:
        data = request.json
        # Stream the request to the backend
        # Note: requests.post with stream=True
        resp = requests.post(f"{BACKEND_URL}/download", json=data, stream=True)
        
        if resp.status_code != 200:
            return jsonify(resp.json()), resp.status_code
            
        # Stream the response back to the client
        # We also want to forward headers like Content-Disposition
        headers = {
            'Content-Disposition': resp.headers.get('Content-Disposition'),
            'Content-Type': resp.headers.get('Content-Type')
        }
        
        return Response(
            resp.iter_content(chunk_size=1024),
            status=resp.status_code,
            headers=headers
        )
    except requests.RequestException as e:
        return jsonify({"error": str(e), "message": "Backend connection failed"}), 502

@app.route('/api/info', methods=['POST'])
def proxy_info():
    try:
        data = request.json
        resp = requests.post(f"{BACKEND_URL}/info", json=data)
        return jsonify(resp.json()), resp.status_code
    except requests.RequestException as e:
        return jsonify({"error": str(e), "message": "Backend connection failed"}), 502

if __name__ == '__main__':
    app.run(port=5000, debug=True)
