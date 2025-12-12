from flask import Flask, render_template, request, jsonify, send_file
from services.downloader import get_info, download_video, clean_url
import os
import threading
import time

app = Flask(__name__)

def remove_file(path: str, delay: int = 1):
    """
    Remove file after a short delay to ensure the file handle is closed.
    """
    def _delete():
        time.sleep(delay)
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"Deleted file: {path}")
        except Exception as e:
            print(f"Error deleting file {path}: {e}")
    
    thread = threading.Thread(target=_delete)
    thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_video_info():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "Missing URL"}), 400
            
        url = data['url']
        cleaned_url = clean_url(url)
        info = get_info(cleaned_url)
        
        return jsonify({
            "title": info.get('title', 'Unknown Title'),
            "id": info.get('id', 'Unknown ID'),
            "webpage_url": info.get('webpage_url', cleaned_url)
        })
    except Exception as e:
        return jsonify({"detail": str(e)}), 400

@app.route('/api/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "Missing URL"}), 400
            
        url = data['url']
        cleaned_url = clean_url(url)
        
        # Download the video
        file_path, title = download_video(cleaned_url)
        
        # Determine filename
        ext = os.path.splitext(file_path)[1]
        filename = f"{title}{ext}"
        
        # Schedule file deletion
        remove_file(file_path, delay=5)
        
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
