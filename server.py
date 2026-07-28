"""Flask dashboard server for live Raspberry Pi camera classifications."""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory

ROOT = Path(__file__).parent
app = Flask(__name__, static_folder=str(ROOT))
lock = threading.Lock()
state = {"label": "Waiting for camera", "confidence": 0, "fps": 0, "updated_at": None}
latest_jpeg: bytes | None = None


@app.get("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.get("/<path:asset>")
def static_asset(asset: str):
    """Serve dashboard assets referenced by index.html (CSS, JavaScript, logo)."""
    return send_from_directory(ROOT, asset)


@app.get("/api/live")
def get_live():
    with lock:
        return jsonify({**state, "has_frame": latest_jpeg is not None})


@app.post("/api/live")
def update_live():
    global latest_jpeg
    payload = request.form if request.form else (request.get_json(silent=True) or {})
    with lock:
        state.update({
            "label": str(payload.get("label", state["label"])),
            "confidence": float(payload.get("confidence", state["confidence"])),
            "fps": float(payload.get("fps", state["fps"])),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        if "frame" in request.files:
            latest_jpeg = request.files["frame"].read()
    return {"ok": True}


@app.get("/api/frame.jpg")
def frame():
    with lock:
        if latest_jpeg is None:
            return "No camera frame yet", 404
        image = latest_jpeg
    return send_file(BytesIO(image), mimetype="image/jpeg", max_age=0)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
