# license_client.py
import os
import json
from pathlib import Path
import requests

SERVER_URL = "http://localhost:8000"  # Change to your FastAPI server URL
LOCAL_LICENSE_FILE = Path.home() / ".genai_premium_local.json"

def save_local_license(token, email):
    LOCAL_LICENSE_FILE.write_text(json.dumps({"token": token, "email": email}))

def load_local_license():
    if LOCAL_LICENSE_FILE.exists():
        return json.loads(LOCAL_LICENSE_FILE.read_text())
    return None

def validate_with_server(token):
    url = f"{SERVER_URL}/validate_token"
    try:
        r = requests.post(url, json={"token": token}, timeout=5)
    except Exception as e:
        return False, {"error": f"server_unreachable: {e}"}
    if r.status_code != 200:
        return False, {"error": f"status_code_{r.status_code}"}
    return r.json().get("valid", False), r.json()
