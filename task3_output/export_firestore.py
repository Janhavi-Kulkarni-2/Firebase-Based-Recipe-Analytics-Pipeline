import firebase_admin
from firebase_admin import credentials, firestore
import json

# Load service account key
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def export_collection(collection_name, file_name=None):
    docs = db.collection(collection_name).stream()
    data = []

    for doc in docs:
        content = doc.to_dict()
        content["id"] = doc.id
        data.append(content)

    file_name = file_name or f"{collection_name}.json"
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Exported {collection_name} → {file_name}")

# Export using EXACT Firestore names
export_collection("Recipes", "recipes.json")
export_collection("Users", "users.json")
export_collection("UserInteractions", "user_interactions.json")
