#!/usr/bin/env python3
"""
visualize.py
Generate charts for the Recipe Analytics project.
Saves PNG files to: task3_output/visuals/
"""

import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Configuration ---
BASE = Path(__file__).resolve().parent  # task3_output
VISUALS = BASE / "visuals"
VISUALS.mkdir(exist_ok=True)

# CSV filenames (expected in task3_output/)
RECIPE_CSV = BASE / "recipe.csv"
ING_CSV = BASE / "ingredients.csv"
INTERACTIONS_CSV = BASE / "interactions.csv"
STEPS_CSV = BASE / "steps.csv"

def read_csv_safe(path):
    if not path.exists():
        raise FileNotFoundError(f"Required CSV not found: {path}")
    return pd.read_csv(path)

def save_fig(fig, name):
    out_path = VISUALS / name
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"Saved: {out_path}")

def top_viewed_recipes(recipes, interactions, top_n=10):
    views = interactions[interactions["type"] == "view"]
    view_counts = views["recipe_id"].value_counts().head(top_n)
    # join with recipe names
    df = view_counts.rename("views").reset_index().rename(columns={"index": "recipe_id"})
    df = df.merge(recipes[["recipe_id", "name"]], on="recipe_id", how="left")
    df = df.sort_values("views", ascending=True)  # for horizontal bar plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(df["name"].fillna(df["recipe_id"]), df["views"])
    ax.set_xlabel("Views")
    ax.set_title(f"Top {len(df)} Most Viewed Recipes")
    save_fig(fig, "most_viewed_recipes.png")

def difficulty_distribution(recipes):
    counts = recipes["difficulty"].fillna("Unknown").value_counts()
    fig, ax = plt.subplots(figsize=(6,6))
    ax.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Difficulty Distribution")
    save_fig(fig, "difficulty_distribution.png")

def most_common_ingredients(ingredients, top_n=15):
    counts = ingredients["ingredient_name"].value_counts().head(top_n)
    fig, ax = plt.subplots(figsize=(8,6))
    counts.sort_values().plot(kind="barh", ax=ax)
    ax.set_xlabel("Recipe Count (ingredient appears in X recipes)")
    ax.set_title(f"Top {len(counts)} Most Common Ingredients")
    save_fig(fig, "most_common_ingredients.png")

def prep_time_vs_likes(recipes, interactions):
    likes = interactions[interactions["type"] == "like"]
    like_counts = likes.groupby("recipe_id").size().rename("like_count").reset_index()
    merged = recipes[["recipe_id", "name", "prep_time_minutes"]].merge(like_counts, on="recipe_id", how="left")
    merged["like_count"] = merged["like_count"].fillna(0)
    # scatter
    fig, ax = plt.subplots(figsize=(7,6))
    ax.scatter(merged["prep_time_minutes"], merged["like_count"])
    ax.set_xlabel("Prep Time (minutes)")
    ax.set_ylabel("Number of Likes")
    ax.set_title("Prep Time vs Likes (per recipe)")

    # add simple linear trendline if there is variation
    if merged["prep_time_minutes"].nunique() > 1:
        x = merged["prep_time_minutes"].values
        y = merged["like_count"].values
        # handle constant arrays
        try:
            coeffs = np.polyfit(x, y, deg=1)
            poly = np.poly1d(coeffs)
            xs = np.linspace(x.min(), x.max(), 100)
            ax.plot(xs, poly(xs), linestyle="--")
        except Exception:
            pass

    save_fig(fig, "prep_time_vs_likes.png")

def top_recipes_by_total_interactions(recipes, interactions, top_n=10):
    total = interactions.groupby("recipe_id").size().rename("total_interactions").reset_index()
    top = total.sort_values("total_interactions", ascending=False).head(top_n)
    df = top.merge(recipes[["recipe_id","name"]], on="recipe_id", how="left").sort_values("total_interactions", ascending=True)
    fig, ax = plt.subplots(figsize=(8,6))
    ax.barh(df["name"].fillna(df["recipe_id"]), df["total_interactions"])
    ax.set_xlabel("Total Interactions")
    ax.set_title(f"Top {len(df)} Recipes by Total Interactions")
    save_fig(fig, "top_recipes_total_interactions.png")

def average_rating_per_recipe(interactions, recipes):
    cook = interactions[interactions["type"] == "cook"].dropna(subset=["rating"])
    if cook.empty:
        print("No cook interactions with ratings found — skipping average_rating_per_recipe.")
        return
    avg = cook.groupby("recipe_id")["rating"].mean().reset_index().sort_values("rating", ascending=False).head(15)
    df = avg.merge(recipes[["recipe_id","name"]], on="recipe_id", how="left")
    fig, ax = plt.subplots(figsize=(8,6))
    ax.bar(df["name"].fillna(df["recipe_id"]), df["rating"])
    ax.set_ylabel("Average Rating")
    ax.set_title("Top Recipes by Average Cook Rating (top 15)")
    ax.set_xticklabels(df["name"].fillna(df["recipe_id"]), rotation=45, ha="right")
    save_fig(fig, "average_rating_per_recipe.png")

def avg_steps_per_recipe(steps):
    counts = steps.groupby("recipe_id").size().rename("step_count").reset_index().sort_values("step_count", ascending=False)
    top = counts.head(15)
    fig, ax = plt.subplots(figsize=(8,6))
    ax.bar(top["recipe_id"], top["step_count"])
    ax.set_xlabel("Recipe ID")
    ax.set_ylabel("Number of Steps")
    ax.set_title("Top Recipes by Number of Steps (top 15)")
    save_fig(fig, "avg_steps_per_recipe.png")

def cuisine_popularity_by_engagement(recipes, interactions):
    eng = interactions.groupby("recipe_id").size().rename("engagement").reset_index()
    merged = eng.merge(recipes[["recipe_id","cuisine"]], on="recipe_id", how="left")
    by_cuisine = merged.groupby("cuisine")["engagement"].sum().sort_values(ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(8,6))
    by_cuisine.sort_values().plot(kind="barh", ax=ax)
    ax.set_xlabel("Total Engagement (views+likes+cooks)")
    ax.set_title("Cuisine Popularity by Engagement")
    save_fig(fig, "cuisine_popularity_engagement.png")

def main():
    try:
        recipes = read_csv_safe(RECIPE_CSV)
        ingredients = read_csv_safe(ING_CSV)
        interactions = read_csv_safe(INTERACTIONS_CSV)
        steps = read_csv_safe(STEPS_CSV)
    except FileNotFoundError as e:
        print(e)
        return

    # Ensure expected column names (common variations handled)
    # rename columns if needed for consistency
    col_map = {}
    if "ingredient_name" not in ingredients.columns and "name" in ingredients.columns:
        col_map["name"] = "ingredient_name"
    if col_map:
        ingredients = ingredients.rename(columns=col_map)

    # Run visualizations
    top_viewed_recipes(recipes, interactions)
    difficulty_distribution(recipes)
    most_common_ingredients(ingredients)
    prep_time_vs_likes(recipes, interactions)
    top_recipes_by_total_interactions(recipes, interactions)
    average_rating_per_recipe(interactions, recipes)
    avg_steps_per_recipe(steps)
    cuisine_popularity_by_engagement(recipes, interactions)

    print("\nAll charts saved to:", VISUALS)

if __name__ == "__main__":
    main()
