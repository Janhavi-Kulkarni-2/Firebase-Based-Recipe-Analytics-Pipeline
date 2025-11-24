from pathlib import Path
import pandas as pd
import json
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Use absolute path relative to analytics.py
BASE = Path(__file__).resolve().parent.parent / "output_csv"

logging.info(f"Loading CSV files from {BASE}...")

# Corrected file names
recipes = pd.read_csv(BASE / "recipe.csv")       # <- plural
ingredients = pd.read_csv(BASE / "ingredients.csv")
steps = pd.read_csv(BASE / "steps.csv")
interactions = pd.read_csv(BASE / "interactions.csv")

logging.info("CSV files loaded successfully.")

# The rest of your analytics code remains the same


insights = {}

# -----------------------------------
# 1. Most common ingredients
# -----------------------------------
logging.info("Computing most common ingredients...")
ing_count = ingredients["ingredient_name"].value_counts().head(10)
insights["most_common_ingredients"] = ing_count.to_dict()

# -----------------------------------
# 2. Average preparation time
# -----------------------------------
insights["average_prep_time_minutes"] = recipes["prep_time_minutes"].mean()

# -----------------------------------
# 3. Difficulty distribution
# -----------------------------------
difficulty_dist = recipes["difficulty"].value_counts()
insights["difficulty_distribution"] = difficulty_dist.to_dict()

# -----------------------------------
# 4. Correlation between prep time & likes
# -----------------------------------
likes = interactions[interactions["type"] == "like"]
likes_count = likes.groupby("recipe_id").size().reset_index(name="like_count")

merged = pd.merge(
    recipes[["recipe_id", "prep_time_minutes"]],
    likes_count,
    on="recipe_id",
    how="left"
)

merged["like_count"] = merged["like_count"].fillna(0)
insights["correlation_prep_time_likes"] = merged["prep_time_minutes"].corr(merged["like_count"])

# -----------------------------------
# 5. Most frequently viewed recipes
# -----------------------------------
views = interactions[interactions["type"] == "view"]
view_count = views["recipe_id"].value_counts().head(10)
insights["most_viewed_recipes"] = view_count.to_dict()

# -----------------------------------
# 6. Ingredients associated with high engagement
# -----------------------------------
engagement = interactions.groupby("recipe_id").size().reset_index(name="engagement")
merged_ing = pd.merge(ingredients, engagement, on="recipe_id", how="left")

ing_engage = (
    merged_ing.groupby("ingredient_name")["engagement"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

insights["high_engagement_ingredients"] = ing_engage.to_dict()

# -----------------------------------
# 7. Average number of steps per recipe
# -----------------------------------
step_count = steps.groupby("recipe_id").size().mean()
insights["avg_steps_per_recipe"] = step_count

# -----------------------------------
# 8. Most time-consuming recipes
# -----------------------------------
recipes["total_time"] = (
    recipes["prep_time_minutes"] + recipes["cook_time_minutes"]
)

top_time = recipes.sort_values(by="total_time", ascending=False).head(10)
insights["most_time_consuming_recipes"] = top_time[
    ["recipe_id", "name", "total_time"]
].to_dict(orient="records")

# -----------------------------------
# 9. Most active users
# -----------------------------------
user_engage = interactions["user_id"].value_counts().head(5)
insights["most_active_users"] = user_engage.to_dict()

# -----------------------------------
# 10. Highest rated recipes
# -----------------------------------
cook = interactions[interactions["type"] == "cook"]

if not cook.empty:
    cook_rating = (
        cook.groupby("recipe_id")["rating"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )
    insights["highest_rated_recipes"] = cook_rating.to_dict()
else:
    insights["highest_rated_recipes"] = {}

# -----------------------------------
# 11. User interaction stats
# -----------------------------------
user_interaction_counts = (
    interactions.groupby(['user_id', 'type'])
    .size()
    .unstack(fill_value=0)
)

insights["user_interaction_counts"] = user_interaction_counts.to_dict(orient="index")

# -----------------------------------
# Save Report
# -----------------------------------
logging.info("Saving analytics_report.json...")

with open("analytics_report.json", "w") as f:
    json.dump(insights, f, indent=4)

logging.info("Analytics complete! See analytics_report.json")
