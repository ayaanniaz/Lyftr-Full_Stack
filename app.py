import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template
from scraper.orchestrator import scrape_url

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})

@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.get_json()
    url = data.get("url")
    result = scrape_url(url)
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(port=8000, debug=True)
