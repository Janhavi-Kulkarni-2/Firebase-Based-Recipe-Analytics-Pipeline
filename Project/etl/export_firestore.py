import firebase_admin
from firebase_admin import credentials, firestore
import json
from pathlib import Path

# Load service account key 
cred = credentials.Certificate("../../serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def export_collection(collection_name, file_name=None):
    docs = db.collection(collection_name).stream()
    data = []

    for doc in docs:
        content = doc.to_dict()
        content["id"] = doc.id
        data.append(content)

    # Determine file name
    file_name = file_name or f"{collection_name}.json"

    # Save into project_root/data/
    output_path = Path("../data") / file_name

    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Exported {collection_name} → {output_path}")

# Export using EXACT Firestore names
export_collection("Recipes", "recipes.json")
export_collection("Users", "users.json")
export_collection("UserInteractions", "user_interactions.json")
