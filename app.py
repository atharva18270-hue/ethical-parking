import os
import requests
import base64
import json

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_NAME = "atharva18270-hue/ethical-parking"  # Your GitHub username/repo
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
        "sha": sha
    }
    requests.put(url, headers=headers, json=payload)
