# transform_etl.py
"""
ETL script to transform exported Firestore JSON into normalized CSVs:
- recipe.csv
- ingredients.csv
- steps.csv
- interactions.csv

Assumptions:
- Input files: recipes.json, users.json, user_interactions.json
- Handles common messy ingredient formats (strings, dicts with different keys)
"""

import json
import pandas as pd
import re
from dateutil import parser as dateparser
from pathlib import Path
import uuid

# ---------- Config ----------
RECIPES_FILE = "../data/recipes.json"
USERS_FILE = "../data/users.json"
INTERACTIONS_FILE = "../data/user_interactions.json"

OUT_RECIPE = "../output_csv/recipe.csv"
OUT_INGRED = "../output_csv/ingredients.csv"
OUT_STEPS = "../output_csv/steps.csv"
OUT_INTERACTIONS = "../output_csv/interactions.csv"

# ---------- Helpers ----------
def safe_get(d, keys, default=None):
    """Try multiple possible keys in dict d."""
    for k in keys:
        if isinstance(d, dict) and k in d:
            return d[k]
    return default

def parse_iso(dt):
    try:
        return dateparser.parse(dt).isoformat()
    except Exception:
        return None

def normalize_ingredient(item):
    """
    Take an ingredient item which may be:
    - dict like {"name": "...", "qty": 1, "unit":"cup"}
    - dict like {"item": "...", "quantity":"1 cup"}
    - string like "1 cup rice" or "Rice"
    Returns a dict: {name, qty_numeric, unit, qty_text}
    """
    result = {"name": None, "qty_numeric": None, "unit": None, "qty_text": None}

    # If it's a dict with typical keys
    if isinstance(item, dict):
        # try common key names
        name = safe_get(item, ["name", "item", "ingredient", "ingredient_name", "label"])
        qty = safe_get(item, ["qty", "quantity", "amount", "qty_numeric", "qty_text"])
        unit = safe_get(item, ["unit", "units", "u", "measure"])
        # name could be nested object
        if isinstance(name, dict):
            name = safe_get(name, ["name", "label"], default=None)
        result["name"] = name if name is not None else None

        # qty may be numeric or string
        if isinstance(qty, (int, float)):
            result["qty_numeric"] = float(qty)
        elif isinstance(qty, str):
            # attempt to pull numeric out of string
            m = re.search(r"([\d.]+)", qty)
            if m:
                try:
                    result["qty_numeric"] = float(m.group(1))
                except:
                    result["qty_numeric"] = None
                result["qty_text"] = qty
            else:
                result["qty_text"] = qty
        else:
            result["qty_text"] = None

        if isinstance(unit, str):
            result["unit"] = unit
        else:
            # if qty field included unit like "1 cup" treat that as qty_text and attempt parse
            if isinstance(qty, str) and result["qty_numeric"] is not None:
                # try extract unit from qty string
                rest = qty[m.end():].strip() if 'm' in locals() else qty
                if rest:
                    result["unit"] = rest
        return result

    # If it's a string like "1 cup rice" or "Rice - 1 cup"
    if isinstance(item, str):
        s = item.strip()
        # attempt to match: qty unit name  OR name qty unit
        # pattern for leading quantity: "1", "1.5", "1/2"
        # handle fractions like "1/2"
        frac = re.match(r"^\s*(\d+\s*/\s*\d+|\d+(\.\d+)?)(?:\s*[-–—]\s*|\s+)([^\n]+)$", s)
        if frac:
            # convert fraction to float if possible
            qty_raw = frac.group(1)
            try:
                if '/' in qty_raw:
                    num, den = qty_raw.split('/')
                    qty_val = float(num) / float(den)
                else:
                    qty_val = float(qty_raw)
                result["qty_numeric"] = qty_val
            except:
                result["qty_numeric"] = None
            rest = frac.group(3).strip()
            # try split unit and name
            parts = rest.split()
            if len(parts) >= 2:
                result["unit"] = parts[0]
                result["name"] = " ".join(parts[1:])
            else:
                result["name"] = rest
            result["qty_text"] = s
            return result

        # Next try pattern "1 cup rice" (leading number)
        m = re.match(r"^\s*(\d+(\.\d+)?)(?:\s+)([^\s]+)(?:\s+)(.+)$", s)
        if m:
            try:
                result["qty_numeric"] = float(m.group(1))
            except:
                result["qty_numeric"] = None
            result["unit"] = m.group(3)
            result["name"] = m.group(4)
            result["qty_text"] = s
            return result

        # Try trailing qty: "Rice 1 cup"
        m2 = re.match(r"^(.+?)\s+(\d+(\.\d+)?)\s*([a-zA-Z%]+)?\s*$", s)
        if m2:
            result["name"] = m2.group(1).strip()
            try:
                result["qty_numeric"] = float(m2.group(2))
            except:
                result["qty_numeric"] = None
            result["unit"] = m2.group(4)
            result["qty_text"] = s
            return result

        # if nothing matched, treat whole string as name
        result["name"] = s
        result["qty_text"] = s
        return result

    # fallback
    result["qty_text"] = str(item)
    result["name"] = str(item)
    return result

# ---------- Load input JSON files ----------
def load_json_file(path):
    p = Path(path)
    if not p.exists():
        print(f"ERROR: {path} not found.")
        return []
    with open(p, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                # some exports produce dict with list under a key, try to find documents list
                # but we expect a list at top level; handle gracefully
                # convert to list if dict had numeric keys
                return [data]
            return data
        except json.JSONDecodeError as e:
            print(f"ERROR decoding {path}: {e}")
            return []

recipes_raw = load_json_file(RECIPES_FILE)
users_raw = load_json_file(USERS_FILE)
interactions_raw = load_json_file(INTERACTIONS_FILE)

print(f"Loaded: {len(recipes_raw)} recipes, {len(users_raw)} users, {len(interactions_raw)} interactions")

# ---------- Transform: Recipes ----------
recipes_rows = []
ingredients_rows = []
steps_rows = []

for r in recipes_raw:
    # try several possible id keys
    recipe_id = safe_get(r, ["recipe_id", "id", "document_id", "doc_id", "name"]) or None
    # If recipe_id still None, fallback to generated uuid
    if not recipe_id or recipe_id == r.get("name"):
        # prefer explicit recipe_id; if not present, use doc id if present
        recipe_id = r.get("recipe_id") or r.get("id") or r.get("name")
    # final fallback
    if not recipe_id:
        recipe_id = "R_" + uuid.uuid4().hex[:8]

    name = safe_get(r, ["name", "title"]) or ""
    description = safe_get(r, ["description", "desc"]) or ""
    servings = safe_get(r, ["servings", "serves"]) or None
    # try both prep_time fields
    prep = safe_get(r, ["prep_time_minutes", "prep_time", "prep_time_mins", "prep_minutes"]) or None
    cook = safe_get(r, ["cook_time_minutes", "cook_time", "cook_time_mins", "cook_minutes"]) or None
    difficulty = safe_get(r, ["difficulty", "level"]) or None
    cuisine = safe_get(r, ["cuisine", "category"]) or None
    created_at = safe_get(r, ["created_at", "createdAt", "created"]) or None
    if created_at:
        created_at = parse_iso(created_at) or created_at

    # Append recipe row
    recipes_rows.append({
        "recipe_id": recipe_id,
        "name": name,
        "description": description,
        "servings": servings,
        "prep_time_minutes": prep,
        "cook_time_minutes": cook,
        "difficulty": difficulty,
        "cuisine": cuisine,
        "created_at": created_at
    })

    # Ingredients: attempt various keys
    raw_ingredients = safe_get(r, ["ingredients", "ingredient_list", "ingredient"]) or []
    # If ingredients is a single string, convert to list
    if isinstance(raw_ingredients, str):
        raw_ingredients = [x.strip() for x in re.split(r"[;,]\s*", raw_ingredients) if x.strip()]
    # If no ingredients but recipe has one-line ingredient-like fields (fallback)
    if not raw_ingredients:
        # try some other keys
        for k in ["items", "components"]:
            if k in r:
                raw_ingredients = r[k] or []
                break

    # Normalize ingredients list
    for ing in raw_ingredients:
        normalized = normalize_ingredient(ing)
        ing_id = "ING_" + uuid.uuid4().hex[:8]
        ingredients_rows.append({
            "ingredient_id": ing_id,
            "recipe_id": recipe_id,
            "ingredient_name": normalized["name"],
            "qty_numeric": normalized["qty_numeric"],
            "unit": normalized["unit"],
            "qty_text": normalized["qty_text"]
        })

    # Steps: allow several possible keys (ordered)
    raw_steps = safe_get(r, ["steps", "instructions", "method", "directions"]) or []
    # If steps stored as a single string, split into sentences
    if isinstance(raw_steps, str):
        # split on sentence terminators or semicolon/newline
        parts = [s.strip() for s in re.split(r"[;\n]|(?<=[.!?])\s+", raw_steps) if s.strip()]
        raw_steps = parts
    # If steps empty but step-like keys exist
    if not raw_steps:
        # maybe r has numbered keys step1, step2
        steps_found = []
        for i in range(1, 21):
            k = f"step_{i}"
            if k in r:
                steps_found.append(r[k])
        if steps_found:
            raw_steps = steps_found

    for idx, step in enumerate(raw_steps, start=1):
        step_id = "STEP_" + uuid.uuid4().hex[:8]
        steps_rows.append({
            "step_id": step_id,
            "recipe_id": recipe_id,
            "step_order": idx,
            "step_text": str(step).strip()
        })

# ---------- Transform: Interactions ----------
inter_rows = []
for it in interactions_raw:
    # keys may vary
    inter_id = safe_get(it, ["interaction_id", "id", "doc_id"]) or None
    if not inter_id:
        inter_id = "I_" + uuid.uuid4().hex[:8]
    user_id = safe_get(it, ["user_id", "user"]) or safe_get(it, ["userId", "uid"]) or None
    recipe_id = safe_get(it, ["recipe_id", "recipe"]) or safe_get(it, ["recipeId"]) or None
    itype = safe_get(it, ["type", "interaction_type", "action"]) or None
    timestamp = safe_get(it, ["timestamp", "time", "created_at", "createdAt"]) or None
    if timestamp:
        timestamp = parse_iso(timestamp) or timestamp
    rating = safe_get(it, ["rating", "score"]) or None

    inter_rows.append({
        "interaction_id": inter_id,
        "user_id": user_id,
        "recipe_id": recipe_id,
        "type": itype,
        "rating": rating,
        "timestamp": timestamp
    })

# ---------- Output DataFrames ----------
df_recipes = pd.DataFrame(recipes_rows).drop_duplicates(subset=["recipe_id"])
df_ingredients = pd.DataFrame(ingredients_rows)
df_steps = pd.DataFrame(steps_rows)
df_interactions = pd.DataFrame(inter_rows)

# Reorder columns nicely
df_recipes = df_recipes[["recipe_id","name","description","servings","prep_time_minutes","cook_time_minutes","difficulty","cuisine","created_at"]]
df_ingredients = df_ingredients[["ingredient_id","recipe_id","ingredient_name","qty_numeric","unit","qty_text"]]
df_steps = df_steps[["step_id","recipe_id","step_order","step_text"]]
df_interactions = df_interactions[["interaction_id","user_id","recipe_id","type","rating","timestamp"]]

# ---------- Save CSVs ----------
df_recipes.to_csv(OUT_RECIPE, index=False)
df_ingredients.to_csv(OUT_INGRED, index=False)
df_steps.to_csv(OUT_STEPS, index=False)
df_interactions.to_csv(OUT_INTERACTIONS, index=False)

print("\nExported CSVs:")
print(f"- {OUT_RECIPE} ({len(df_recipes)} recipes)")
print(f"- {OUT_INGRED} ({len(df_ingredients)} ingredients rows)")
print(f"- {OUT_STEPS} ({len(df_steps)} steps rows)")
print(f"- {OUT_INTERACTIONS} ({len(df_interactions)} interactions rows)")

# ---------- Basic sanity checks ----------
errors = []

# Check required fields in recipes
for _, row in df_recipes.iterrows():
    if not row["recipe_id"] or not row["name"]:
        errors.append(f"Recipe missing id or name: {row.to_dict()}")

# Check ingredient non-empty name
for _, row in df_ingredients.iterrows():
    if not row["ingredient_name"] or str(row["ingredient_name"]).strip()=="":
        errors.append(f"Ingredient missing name for recipe {row['recipe_id']} (ingredient_id {row['ingredient_id']})")

# Report
if errors:
    print("\nWARNINGS/ISSUES found:")
    for e in errors[:50]:
        print("-", e)
else:
    print("\nNo obvious issues found in basic checks.")
