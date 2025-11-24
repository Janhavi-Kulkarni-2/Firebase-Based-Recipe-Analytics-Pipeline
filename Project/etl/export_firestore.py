# Project/etl/export_firestore.py
"""
Export Firestore collections to Project/data/*.json
Usage: python export_firestore.py
"""

import json
from pathlib import Path
import logging
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# --- Paths ---
# PROJECT_DIR = Project/
PROJECT_DIR = Path(__file__).resolve().parents[1]

# data folder inside Project/
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# serviceAccountKey.json is stored in repo root (one level above Project)
SERVICE_KEY = PROJECT_DIR.parent / "serviceAccountKey.json"

# Validate Key Exists
if not SERVICE_KEY.exists():
    logging.error(f"Service account key not found at: {SERVICE_KEY}")
    logging.error("Move your serviceAccountKey.json into the firebase_recipe_pipeline/ folder.")
    sys.exit(1)

logging.info(f"Using service account: {SERVICE_KEY}")

# Initialize Firebase
try:
    cred = credentials.Certificate(str(SERVICE_KEY))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    logging.error("Failed to initialize Firebase Admin: %s", e)
    sys.exit(1)

def export_collection(collection_name: str, file_name: str = None):
    file_name = file_name or f"{collection_name}.json"
    out_path = DATA_DIR / file_name
    docs = db.collection(collection_name).stream()
    data = []
    count = 0
    for doc in docs:
        d = doc.to_dict() or {}
        d["_doc_id"] = doc.id
        data.append(d)
        count += 1
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info("Exported %s → %s (%d documents)", collection_name, out_path, count)

if __name__ == "__main__":
    # export exact collection names used in your project
    export_collection("Recipes", "recipes.json")
    export_collection("Users", "users.json")
    export_collection("UserInteractions", "user_interactions.json")
    logging.info("All exports complete.")
