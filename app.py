import os
import requests
import base64
import json
from flask import Flask, render_template, request, jsonify  # Make sure 'app' is defined here!

app = Flask(__name__)  # <-- This is what Gunicorn looks for!

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_NAME = "atharva18270-hue/ethical-parking"
FILE_PATH = "data.json"

def get_github_data():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_content = response.json()
        decoded_content = base64.b64decode(file_content["content"]).decode("utf-8")
        return json.loads(decoded_content), file_content["sha"]
    return [], None

def save_to_github(new_record):
    data, sha = get_github_data()
    data.insert(0, new_record)  # Add new booking to the top
    
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    
    updated_content = base64.b64encode(json.dumps(data, indent=2).encode("utf-8")).decode("utf-8")
    
    payload = {
        "message": "Update parking ledger data.json",
        "content": updated_content,
        "sha": sha  # Required by GitHub so it knows which version to overwrite
    }
    
    response = requests.put(url, headers=headers, json=payload)
    
    # Print out what GitHub says so we can see it in Render logs
    print("GitHub Save Status Code:", response.status_code)
    print("GitHub Response:", response.text)
# --- Your Flask Routes Go Below ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/ledger", methods=["GET"])
def get_ledger():
    data, _ = get_github_data()
    return jsonify(data)

# (And your booking route that calls save_to_github(new_record) when someone parks!)

if __name__ == "__main__":
    app.run(debug=True)
