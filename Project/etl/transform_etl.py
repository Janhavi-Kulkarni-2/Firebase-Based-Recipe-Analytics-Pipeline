# Project/etl/transform_etl.py
"""
Transform exported Firestore JSON (Project/data/*.json) into normalized CSVs:
 - Project/output_csv/recipe.csv
 - Project/output_csv/ingredients.csv
 - Project/output_csv/steps.csv
 - Project/output_csv/interactions.csv

Usage: python transform_etl.py
"""

import json
import re
import uuid
from pathlib import Path
import logging
from dateutil import parser as dateparser
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
OUT_DIR = PROJECT_DIR / "output_csv"
OUT_DIR.mkdir(parents=True, exist_ok=True)

RECIPES_FILE = DATA_DIR / "recipes.json"
USERS_FILE = DATA_DIR / "users.json"
INTERACTIONS_FILE = DATA_DIR / "user_interactions.json"

def load_json(path: Path):
    if not path.exists():
        logging.warning("Not found: %s (returning empty list)", path)
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
        except Exception as e:
            logging.error("Failed to parse JSON %s: %s", path, e)
            return []

def safe_get(d, keys, default=""):
    if not isinstance(d, dict):
        return default
    for k in keys:
        if k in d and d[k] not in (None, "NaN"):
            return d[k]
    return default

def parse_iso(dt):
    if not dt:
        return ""
    try:
        return dateparser.parse(dt).isoformat()
    except Exception:
        return str(dt)

def normalize_ingredient(item):
    # return dict: name, qty_numeric (float), unit, qty_text
    out = {"name": "", "qty_numeric": 0.0, "unit": "", "qty_text": ""}
    if isinstance(item, dict):
        out["name"] = safe_get(item, ["name", "ingredient_name", "item", "label"], "") or ""
        qty = safe_get(item, ["qty", "quantity", "qty_numeric", "amount", "qty_text"], "")
        if isinstance(qty, (int, float)):
            out["qty_numeric"] = float(qty)
        elif isinstance(qty, str):
            m = re.search(r"([\d.]+)", qty)
            if m:
                try:
                    out["qty_numeric"] = float(m.group(1))
                except:
                    out["qty_numeric"] = 0.0
                out["qty_text"] = qty
            else:
                out["qty_text"] = qty
        out["unit"] = safe_get(item, ["unit", "units", "measure"], "") or ""
        return out
    if isinstance(item, str):
        s = item.strip()
        out["qty_text"] = s
        m = re.match(r"^(\d+(\.\d+)?)(?:\s+)([^\s]+)(?:\s+)(.+)$", s)
        if m:
            try:
                out["qty_numeric"] = float(m.group(1))
            except:
                out["qty_numeric"] = 0.0
            out["unit"] = m.group(3)
            out["name"] = m.group(4)
            return out
        out["name"] = s
        return out
    return out

# Load
recipes_raw = load_json(RECIPES_FILE)
users_raw = load_json(USERS_FILE)
inter_raw = load_json(INTERACTIONS_FILE)
logging.info("Loaded: %d recipes, %d users, %d interactions", len(recipes_raw), len(users_raw), len(inter_raw))

# Transform recipes / ingredients / steps
recipes_rows = []
ingredients_rows = []
steps_rows = []

for r in recipes_raw:
    rid = safe_get(r, ["recipe_id", "id", "_doc_id"], "") or ("R_" + uuid.uuid4().hex[:8])
    name = safe_get(r, ["name", "title"], "")
    recipes_rows.append({
        "recipe_id": rid,
        "name": name,
        "description": safe_get(r, ["description", "desc"], ""),
        "servings": safe_get(r, ["servings", "serves"], 0) or 0,
        "prep_time_minutes": safe_get(r, ["prep_time_minutes", "prep_time", "prep_minutes"], 0) or 0,
        "cook_time_minutes": safe_get(r, ["cook_time_minutes", "cook_time", "cook_minutes"], 0) or 0,
        "difficulty": safe_get(r, ["difficulty", "level"], ""),
        "cuisine": safe_get(r, ["cuisine", "category"], ""),
        "created_at": parse_iso(safe_get(r, ["created_at", "createdAt"], ""))
    })

    raw_ing = safe_get(r, ["ingredients", "ingredient_list", "ingredient"], [])
    if isinstance(raw_ing, str):
        raw_ing = [x.strip() for x in re.split(r"[;,]\s*", raw_ing) if x.strip()]
    for ing in raw_ing or []:
        n = normalize_ingredient(ing)
        ingredients_rows.append({
            "ingredient_id": "ING_" + uuid.uuid4().hex[:8],
            "recipe_id": rid,
            "ingredient_name": n["name"],
            "qty_numeric": n["qty_numeric"],
            "unit": n["unit"],
            "qty_text": n["qty_text"]
        })

    raw_steps = safe_get(r, ["steps", "instructions", "method", "directions"], [])
    if isinstance(raw_steps, str):
        raw_steps = [s.strip() for s in re.split(r"[;\n]|(?<=[.!?])\s+", raw_steps) if s.strip()]
    for i, st in enumerate(raw_steps or [], start=1):
        steps_rows.append({
            "step_id": "STEP_" + uuid.uuid4().hex[:8],
            "recipe_id": rid,
            "step_order": i,
            "step_text": str(st).strip()
        })

# Transform interactions
inter_rows = []
for it in inter_raw:
    inter_rows.append({
        "interaction_id": safe_get(it, ["interaction_id", "id", "_doc_id"], "I_" + uuid.uuid4().hex[:8]),
        "user_id": safe_get(it, ["user_id", "user", "uid"], ""),
        "recipe_id": safe_get(it, ["recipe_id", "recipe"], ""),
        "type": safe_get(it, ["type", "action", "interaction_type"], ""),
        "rating": safe_get(it, ["rating", "score"], "") if safe_get(it, ["type"], "") == "cook" else "",
        "timestamp": parse_iso(safe_get(it, ["timestamp", "time", "created_at"], ""))
    })

# DataFrames & save (no NaN)
df_recipes = pd.DataFrame(recipes_rows).fillna("").astype(object)
df_ingredients = pd.DataFrame(ingredients_rows).fillna("").astype(object)
df_steps = pd.DataFrame(steps_rows).fillna("").astype(object)
df_interactions = pd.DataFrame(inter_rows).fillna("").astype(object)

df_recipes.to_csv(OUT_DIR / "recipe.csv", index=False)
df_ingredients.to_csv(OUT_DIR / "ingredients.csv", index=False)
df_steps.to_csv(OUT_DIR / "steps.csv", index=False)
df_interactions.to_csv(OUT_DIR / "interactions.csv", index=False)

logging.info("Wrote CSVs to %s (recipes=%d, ingredients=%d, steps=%d, interactions=%d)",
             OUT_DIR, len(df_recipes), len(df_ingredients), len(df_steps), len(df_interactions))
