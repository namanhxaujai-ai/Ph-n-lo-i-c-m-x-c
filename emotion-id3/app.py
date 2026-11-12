import os

from flask import Flask, jsonify, request, send_from_directory

import model
from data import DEFAULT_DATA

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024


def _strategy(payload):
    value = (payload or {}).get("strategy", "bfs")
    if value not in ("bfs", "dfs"):
        raise ValueError("strategy phải là bfs hoặc dfs")
    return value


@app.errorhandler(ValueError)
def bad_request(err):
    return jsonify({"error": str(err)}), 400


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/dataset")
def dataset():
    return jsonify({"data": DEFAULT_DATA})


@app.post("/api/train")
def train():
    payload = request.get_json(silent=True) or {}
    data = payload.get("data", DEFAULT_DATA)
    return jsonify(model.full_report(data, _strategy(payload)))


@app.post("/api/predict")
def predict():
    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text", "")).strip()
    if not text:
        raise ValueError("Hãy nhập một câu")
    data = payload.get("data", DEFAULT_DATA)
    return jsonify(model.classify(data, text[:300], _strategy(payload)))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
