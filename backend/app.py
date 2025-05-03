import os
import json
import uuid
import importlib
import threading
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

app = Flask(__name__, static_folder="./frontend/build", template_folder="./frontend/build")
CORS(app)

# Store task results in memory
results = {}

# Serve React static files
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    full_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

# List all scraper modules
@app.route("/api/scrapers")
def list_scrapers():
    modules_dir = os.path.join(os.path.dirname(__file__), "modules")
    scrapers = [
        d for d in os.listdir(modules_dir)
        if os.path.isdir(os.path.join(modules_dir, d))
    ]
    return jsonify(scrapers)

# Load scraper config (hashamx.json)
@app.route("/api/scraper/<scraperName>")
def get_scraper(scraperName):
    try:
        module_path = os.path.join("modules", scraperName, "hashamx.json")
        with open(module_path, "r") as f:
            config = json.load(f)
        return jsonify({
            "fields": config["input"]["fields"],
            "header": config["input"]["header"],
            "name": config["name"],
            "description": config["description"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Background scraper runner
def run_scraper_task(scraper_name, data, task_id):
    try:
        module = importlib.import_module(f"modules.{scraper_name}.scraper")
        scraper_class = getattr(module, scraper_name)
        scraper = scraper_class(**data)
        total_items, items = scraper.scrape()
        results[task_id] = {
            "status": "done",
            "data": {"total_items": total_items, "items": items}
        }
    except Exception as e:
        results[task_id] = {
            "status": "error",
            "error": str(e)
        }

# Start scraper in background
@app.route("/api/run-scraper", methods=["POST"])
def run_scraper():
    req = request.get_json()
    scraper_name = req.get("scraper")
    data = req.get("data", {})

    task_id = str(uuid.uuid4())
    results[task_id] = {"status": "running"}

    thread = threading.Thread(target=run_scraper_task, args=(scraper_name, data, task_id))
    thread.daemon = True
    thread.start()

    return jsonify({"task_id": task_id})

# Poll task status
@app.route("/api/status/<task_id>")
def check_status(task_id):
    result = results.get(task_id)
    if not result:
        return jsonify({"error": "Task not found"}), 404
    response = jsonify(result)
    if result["status"] in ("done", "error"):
        del results[task_id]
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
