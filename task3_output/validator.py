import pandas as pd
import json
from pathlib import Path

BASE = Path("task3_output")


# -----------------------------
read_opts = dict(keep_default_na=False, na_values=[''])

recipes = pd.read_csv(BASE / "recipe.csv", **read_opts)
ingredients = pd.read_csv(BASE / "ingredients.csv", **read_opts)
steps = pd.read_csv(BASE / "steps.csv", **read_opts)
interactions = pd.read_csv(BASE / "interactions.csv", **read_opts)

report = {
    "recipes": {"valid": [], "invalid": []},
    "ingredients": {"valid": [], "invalid": []},
    "steps": {"valid": [], "invalid": []},
    "interactions": {"valid": [], "invalid": []},
}

# ------------------------------------
# VALIDATION FUNCTIONS
# ------------------------------------

def is_positive_number(value):
    if value == "" or value is None:
        return False
    try:
        return float(value) >= 0
    except:
        return False

def validate_recipes():
    for idx, row in recipes.iterrows():
        errors = []

        if row["recipe_id"] == "":
            errors.append("Missing recipe_id")
        if row["name"] == "":
            errors.append("Missing name")
        if row["difficulty"] == "":
            errors.append("Missing difficulty")

        if row["difficulty"] not in ["Easy", "Medium", "Hard"]:
            errors.append("Invalid difficulty")

        for col in ["servings", "prep_time_minutes", "cook_time_minutes"]:
            if not is_positive_number(row[col]):
                errors.append(f"Invalid {col} (must be positive number)")

        if errors:
            report["recipes"]["invalid"].append({**row.to_dict(), "errors": errors})
        else:
            report["recipes"]["valid"].append(row.to_dict())

def validate_ingredients():
    for idx, row in ingredients.iterrows():
        errors = []

        if row["ingredient_id"] == "":
            errors.append("Missing ingredient_id")
        if row["recipe_id"] == "":
            errors.append("Missing recipe_id")
        if row["ingredient_name"] == "":
            errors.append("Missing ingredient_name")

        qty = row["qty_numeric"]
        if qty != "":
            try:
                if float(qty) < 0:
                    errors.append("qty_numeric cannot be negative")
            except:
                errors.append("qty_numeric must be numeric")

        if errors:
            report["ingredients"]["invalid"].append({**row.to_dict(), "errors": errors})
        else:
            report["ingredients"]["valid"].append(row.to_dict())

def validate_steps():
    for idx, row in steps.iterrows():
        errors = []

        if row["step_id"] == "":
            errors.append("Missing step_id")
        if row["recipe_id"] == "":
            errors.append("Missing recipe_id")
        if row["step_text"] == "":
            errors.append("Missing step_text")

        try:
            if int(row["step_order"]) < 1:
                errors.append("step_order must be ≥ 1")
        except:
            errors.append("step_order must be integer")

        if errors:
            report["steps"]["invalid"].append({**row.to_dict(), "errors": errors})
        else:
            report["steps"]["valid"].append(row.to_dict())

def validate_interactions():
    for idx, row in interactions.iterrows():
        errors = []

        if row["interaction_id"] == "":
            errors.append("Missing interaction_id")
        if row["user_id"] == "":
            errors.append("Missing user_id")
        if row["recipe_id"] == "":
            errors.append("Missing recipe_id")
        if row["type"] == "":
            errors.append("Missing type")

        if row["type"] not in ["view", "like", "cook"]:
            errors.append("Invalid type")

        rating = row["rating"]

        if row["type"] == "cook":
            try:
                r = float(rating)
                if not (1 <= r <= 5):
                    errors.append("Cook rating must be between 1 and 5")
            except:
                errors.append("Cook must have numeric rating")
        else:
            if rating not in ["", None]:
                errors.append("Non-cook interaction should not have rating")

        if errors:
            report["interactions"]["invalid"].append({**row.to_dict(), "errors": errors})
        else:
            report["interactions"]["valid"].append(row.to_dict())

# Run all validations
validate_recipes()
validate_ingredients()
validate_steps()
validate_interactions()

# Save report
with open(BASE / "validation_report.json", "w") as f:
    json.dump(report, f, indent=4)

print("Validation complete! Open validation_report.json for details.")
