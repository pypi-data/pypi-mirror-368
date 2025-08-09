#!/usr/bin/env python3
from flask import Flask, request, send_file, jsonify
import os
from .downloader import validate_environment, download_video

app = Flask(__name__)
DOWNLOAD_DIR = "/root"

@app.route('/api/download', methods=['POST'])
def handle_download():
    data = request.get_json(force=True)
    url = data.get("url")
    resolution = data.get("resolution")
    extension = data.get("extension")

    if not url:
        return jsonify(error="Missing 'url'"), 400

    try:
        filename = download_video(
            url=url,
            resolution=resolution,
            extension=extension
        )

        if filename and os.path.exists(filename):
            return send_file(filename, as_attachment=True)
        else:
            return jsonify(error="Download failed"), 500

    except RuntimeError as e:
        # Surface “not logged in” or environment errors cleanly
        msg = str(e)
        # If Mullvad not logged in yet, return 503 so callers can show a helpful message
        if "Mullvad is not logged in" in msg:
            return jsonify(error=msg), 503
        return jsonify(error=f"Download failed: {msg}"), 500
    except Exception as e:
        return jsonify(error=f"Download failed: {str(e)}"), 500

def main():
    """Entry point for the API server (dev only). Use Gunicorn in production."""
    validate_environment()  # Ensure we're in the correct environment
    print("Starting ytp-dl API server...")
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
