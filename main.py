"""
task2_firestore_upload_fixed.py
Corrected Task 2 uploader: inserts Veg Pulav + 19 synthetic recipes,
5 users, and 50 interactions with consistent schema and field names.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
import random
import uuid

# ---------------------------
# Initialize Firebase Admin
# ---------------------------
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Helper for ISO timestamp (UTC with Z)
def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# ---------------------------
# 1) Veg Pulav (primary dataset)
# ---------------------------
veg_pulav = {
    "recipe_id": "R001",
    "name": "Veg Pulav",
    "description": "Fluffy rice cooked with mixed vegetables and pulav masala. Great as a one-pot meal.",
    "servings": 2,
    "prep_time_minutes": 15,
    "cook_time_minutes": 20,
    "difficulty": "Easy",
    "ingredients": [
        {"name": "Rice", "qty": 1.0, "unit": "cup"},
        {"name": "Water", "qty": 3.5, "unit": "cups"},
        {"name": "Oil/Butter", "qty": 1.0, "unit": "tbsp"},
        {"name": "Salt", "qty": 1.0, "unit": "tsp"},
        {"name": "Pulav Masala", "qty": 1.0, "unit": "tsp"},
        {"name": "Cauliflower", "qty": 0.25, "unit": "cup"},
        {"name": "Green Beans", "qty": 0.25, "unit": "cup"},
        {"name": "Carrot", "qty": 0.25, "unit": "cup"},
        {"name": "Onion", "qty": 0.5, "unit": "medium"},
        {"name": "Tomato", "qty": 1.0, "unit": "medium"},
        {"name": "Green Chillies", "qty": 1.0, "unit": "pcs"},
        {"name": "Fresh Coriander", "qty": 1.0, "unit": "tbsp"}
    ],
    "steps": [
        "Rinse rice under running water until water runs clear; soak for 10–15 minutes and drain.",
        "Wash and chop cauliflower, beans, carrot, onion, tomato and green chillies.",
        "Heat oil or butter in a pressure cooker on medium heat.",
        "Add sliced onion and sauté until slightly soft (about 1 minute).",
        "Add carrot, beans, cauliflower, green chillies and tomato; sauté 3–4 minutes until slightly tender.",
        "Add drained rice and mix gently with vegetables — do not break rice grains.",
        "Add water (3–4 cups), salt and pulav masala; stir gently to combine.",
        "Close the pressure cooker lid and cook for 1–2 whistles on medium heat; turn off and let pressure release naturally. (If using pot: cover and simmer 15–20 minutes until rice is cooked.)",
        "Open carefully, fluff rice gently with a spatula, garnish with chopped coriander and serve hot."
    ],
    "cuisine": "Indian",
    "created_at": now_iso()
}

# Upload Veg Pulav
db.collection("Recipes").document(veg_pulav["recipe_id"]).set(veg_pulav)
print("Uploaded Veg Pulav (R001)")

# ---------------------------
# 2) Generate 19 synthetic recipes (R002..R020)
# ---------------------------
sample_recipe_templates = [
    {
        "name": "Tomato Basil Soup",
        "description": "Creamy tomato soup with fresh basil.",
        "cuisine": "International",
        "base_ingredients": [
            ("Tomato", 4, "pcs"),
            ("Water", 2, "cups"),
            ("Butter", 1, "tbsp"),
            ("Cream", 2, "tbsp")
        ]
    },
    {
        "name": "Masala Dosa",
        "description": "Crispy dosa with spiced mashed potatoes.",
        "cuisine": "Indian",
        "base_ingredients": [
            ("Dosa batter", 2, "cups"),
            ("Potato", 2, "pcs"),
            ("Onion", 1, "medium"),
            ("Turmeric", 0.5, "tsp")
        ]
    },
    {
        "name": "Pasta Alfredo",
        "description": "Creamy white-sauce pasta.",
        "cuisine": "Italian",
        "base_ingredients": [
            ("Pasta", 200, "g"),
            ("Butter", 2, "tbsp"),
            ("Cream", 100, "ml"),
            ("Parmesan", 50, "g")
        ]
    },
    {
        "name": "Chickpea Salad",
        "description": "Refreshing salad with chickpeas and veggies.",
        "cuisine": "Mediterranean",
        "base_ingredients": [
            ("Chickpeas", 1, "cup"),
            ("Cucumber", 0.5, "cup"),
            ("Tomato", 1, "medium"),
            ("Olive Oil", 1, "tbsp")
        ]
    },
    {
        "name": "Paneer Butter Masala",
        "description": "Rich and creamy paneer curry.",
        "cuisine": "Indian",
        "base_ingredients": [
            ("Paneer", 200, "g"),
            ("Tomato", 2, "pcs"),
            ("Butter", 2, "tbsp"),
            ("Cream", 2, "tbsp")
        ]
    },
    {
        "name": "Stir-fry Vegetables",
        "description": "Quick wok-tossed mixed vegetables.",
        "cuisine": "Chinese",
        "base_ingredients": [
            ("Broccoli", 1, "cup"),
            ("Carrot", 1, "cup"),
            ("Soy Sauce", 1, "tbsp"),
            ("Garlic", 2, "cloves")
        ]
    }
]

# We'll reuse templates and vary prep/cook times & difficulty
for idx in range(2, 21):  # 2..20 => 19 recipes
    tidx = random.randrange(len(sample_recipe_templates))
    t = sample_recipe_templates[tidx]
    recipe_id = f"R{idx:03}"
    # create ingredient list: base ingredients + 1-2 random extra
    ingredients = []
    for name, qty, unit in t["base_ingredients"]:
        # keep numeric qty where possible
        ingredients.append({"name": name, "qty": qty if isinstance(qty, (int, float)) else qty, "unit": unit})
    # optional extras
    extras = [
        ("Salt", 1, "tsp"),
        ("Pepper", 0.5, "tsp"),
        ("Coriander", 1, "tbsp"),
        ("Olive Oil", 1, "tbsp"),
        ("Green Chili", 1, "pcs")
    ]
    extra_count = random.choice([0, 1, 2])
    for e in random.sample(extras, extra_count):
        ingredients.append({"name": e[0], "qty": e[1], "unit": e[2]})

    prep = random.randint(5, 30)
    cook = random.randint(5, 45)
    diff = random.choice(["Easy", "Medium", "Hard"])
    steps = [
        f"Prepare ingredients for {t['name']}.",
        "Combine and cook base ingredients as required.",
        "Season and simmer until done.",
        "Serve hot."
    ]

    recipe = {
        "recipe_id": recipe_id,
        "name": t["name"] + (f" {idx}" if idx % 3 == 0 else ""),  # slight variation
        "description": t["description"],
        "servings": random.randint(1, 6),
        "prep_time_minutes": prep,
        "cook_time_minutes": cook,
        "difficulty": diff,
        "ingredients": ingredients,
        "steps": steps,
        "cuisine": t["cuisine"],
        "created_at": now_iso()
    }

    db.collection("Recipes").document(recipe_id).set(recipe)

print("Uploaded 19 synthetic recipes (R002..R020)")

# ---------------------------
# 3) Create Users (5)
# ---------------------------
users = [
    {"user_id": "U001", "name": "Janhavi", "email": "janhavi@example.com", "joined_at": now_iso()},
    {"user_id": "U002", "name": "Amit", "email": "amit@example.com", "joined_at": now_iso()},
    {"user_id": "U003", "name": "Neha", "email": "neha@example.com", "joined_at": now_iso()},
    {"user_id": "U004", "name": "Rohan", "email": "rohan@example.com", "joined_at": now_iso()},
    {"user_id": "U005", "name": "Priya", "email": "priya@example.com", "joined_at": now_iso()}
]

for u in users:
    db.collection("Users").document(u["user_id"]).set(u)

print("Uploaded 5 users (U001..U005)")

# ---------------------------
# 4) Generate 50 Interactions
# ---------------------------
interaction_types = ["view", "like", "cook"]
interactions_to_create = 50
created_interactions = []

recipe_ids = [f"R{n:03}" for n in range(1, 21)]  # R001..R020
user_ids = [u["user_id"] for u in users]

for i in range(1, interactions_to_create + 1):
    iid = f"I{i:04}"  # I0001...
    chosen_user = random.choice(user_ids)
    chosen_recipe = random.choice(recipe_ids)
    itype = random.choices(interaction_types, weights=[0.6, 0.25, 0.15])[0]  # more views than likes/cooks
    interaction = {
        "interaction_id": iid,
        "user_id": chosen_user,
        "recipe_id": chosen_recipe,
        "type": itype,
        "timestamp": now_iso()
    }
    if itype == "cook":
        interaction["rating"] = random.randint(1, 5)
    created_interactions.append(interaction)
    db.collection("UserInteractions").document(iid).set(interaction)

print(f"Uploaded {interactions_to_create} interactions (I0001..I{interactions_to_create:04})")

print("\n Task 2 (fixed) completed: Recipes, Users, UserInteractions inserted with consistent schema.")


