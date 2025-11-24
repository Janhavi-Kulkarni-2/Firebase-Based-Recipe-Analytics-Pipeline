# Project/etl/validator.py
"""
Validate CSV outputs in Project/output_csv/
Usage: python validator.py
"""

import pandas as pd
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_DIR / "output_csv"

if not OUT_DIR.exists():
    logging.error("Output CSV directory not found: %s", OUT_DIR)
    raise SystemExit(1)

def read_csv_no_nan(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])
    return df.fillna("").replace({"NaN": ""})

recipes = read_csv_no_nan(OUT_DIR / "recipe.csv")
ingredients = read_csv_no_nan(OUT_DIR / "ingredients.csv")
steps = read_csv_no_nan(OUT_DIR / "steps.csv")
interactions = read_csv_no_nan(OUT_DIR / "interactions.csv")

report = {"recipes": {"valid": [], "invalid": []},
          "ingredients": {"valid": [], "invalid": []},
          "steps": {"valid": [], "invalid": []},
          "interactions": {"valid": [], "invalid": []}}

def is_nonneg_number(s):
    try:
        return float(s) >= 0
    except:
        return False

# --- validations (same rules as before) ---
def validate_recipes():
    for _, r in recipes.iterrows():
        errors = []
        if r.get("recipe_id", "") == "":
            errors.append("Missing recipe_id")
        if r.get("name", "") == "":
            errors.append("Missing name")
        diff = r.get("difficulty", "")
        if diff == "":
            errors.append("Missing difficulty")
        if diff and diff not in ["Easy", "Medium", "Hard"]:
            errors.append("Invalid difficulty")
        for col in ["servings", "prep_time_minutes", "cook_time_minutes"]:
            if not is_nonneg_number(r.get(col, "")):
                errors.append(f"Invalid {col}")
        if errors:
            report["recipes"]["invalid"].append({**r.to_dict(), "errors": errors})
        else:
            report["recipes"]["valid"].append(r.to_dict())

def validate_ingredients():
    for _, r in ingredients.iterrows():
        errors = []
        if r.get("ingredient_id", "") == "":
            errors.append("Missing ingredient_id")
        if r.get("recipe_id", "") == "":
            errors.append("Missing recipe_id")
        if r.get("ingredient_name", "") == "":
            errors.append("Missing ingredient_name")
        qty = r.get("qty_numeric", "")
        if qty != "":
            try:
                if float(qty) < 0:
                    errors.append("qty_numeric negative")
            except:
                errors.append("qty_numeric not numeric")
        if errors:
            report["ingredients"]["invalid"].append({**r.to_dict(), "errors": errors})
        else:
            report["ingredients"]["valid"].append(r.to_dict())

def validate_steps():
    for _, r in steps.iterrows():
        errors = []
        if r.get("step_id", "") == "":
            errors.append("Missing step_id")
        if r.get("recipe_id", "") == "":
            errors.append("Missing recipe_id")
        if r.get("step_text", "") == "":
            errors.append("Missing step_text")
        try:
            if int(r.get("step_order", "0")) < 1:
                errors.append("step_order must be >=1")
        except:
            errors.append("step_order not integer")
        if errors:
            report["steps"]["invalid"].append({**r.to_dict(), "errors": errors})
        else:
            report["steps"]["valid"].append(r.to_dict())

def validate_interactions():
    for _, r in interactions.iterrows():
        errors = []
        if r.get("interaction_id", "") == "":
            errors.append("Missing interaction_id")
        if r.get("user_id", "") == "":
            errors.append("Missing user_id")
        if r.get("recipe_id", "") == "":
            errors.append("Missing recipe_id")
        t = r.get("type", "")
        if t == "":
            errors.append("Missing type")
        if t and t not in ["view", "like", "cook"]:
            errors.append("Invalid type")
        rating = r.get("rating", "")
        if t == "cook":
            try:
                val = float(rating)
                if not (1 <= val <= 5):
                    errors.append("rating must be 1-5")
            except:
                errors.append("cook rating not numeric")
        else:
            if rating not in ["", None]:
                errors.append("non-cook interaction should not have rating")
        if errors:
            report["interactions"]["invalid"].append({**r.to_dict(), "errors": errors})
        else:
            report["interactions"]["valid"].append(r.to_dict())

# Run
validate_recipes()
validate_ingredients()
validate_steps()
validate_interactions()

OUT_REPORT = OUT_DIR / "validation_report.json"
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

logging.info("Validation complete. Report saved: %s", OUT_REPORT)
