Firebase-Based Recipe Analytics Pipeline

This project is a complete recipe management and analytics pipeline using Firebase Firestore, Python, and Pandas.
It allows you to:

Add recipes, users, and interactions

Validate the data

Perform analytics

Generate insights with a clean ETL process

Table of Contents

Data Model

Pipeline Instructions

ETL Process Overview

Analytics & Insights

Visualization

Known Limitations

Future Enhancements

1. Data Model

The data model is designed to efficiently capture recipes, users, and interactions for analytics, validation, and ETL processing.

A. Recipes Collection

Stores details of each recipe. Each recipe has a unique recipe_id (Primary Key).

Fields:

name: Name of the recipe

description: Short description

servings: Number of servings

prep_time_minutes & cook_time_minutes: Cooking times

difficulty: Difficulty level (Easy, Medium, Hard)

cuisine: Cuisine type (e.g., Indian, Italian, Chinese)

ingredients: Array of objects (name, qty_numeric, unit, qty_text)

steps: Array of objects (step_order, step_text)

created_at: Timestamp

Example:

{
  "recipe_id": "R001",
  "name": "Veg Pulav",
  "description": "Fluffy rice with vegetables and spices.",
  "servings": 2,
  "prep_time_minutes": 15,
  "cook_time_minutes": 20,
  "difficulty": "Easy",
  "ingredients": [
    {"name": "Rice", "qty_numeric": 1.0, "unit": "cup", "qty_text": ""},
    {"name": "Water", "qty_numeric": 3.5, "unit": "cups", "qty_text": ""}
  ],
  "steps": [
    {"step_order": 1, "step_text": "Rinse rice under running water."},
    {"step_order": 2, "step_text": "Chop vegetables."}
  ],
  "cuisine": "Indian",
  "created_at": "2025-11-20T06:00:00Z"
}


Schema Image:


B. Users Collection

Stores information about registered users.

Fields:

user_id: Unique identifier

name: User’s name

email: User’s email

joined_at: Timestamp

Example:

{
  "user_id": "U001",
  "name": "Janhavi",
  "email": "janhavi@example.com",
  "joined_at": "2025-11-20T06:00:00Z"
}


Schema Image:


C. UserInteractions Collection

Records how users interact with recipes.

Fields:

interaction_id: Unique ID for interaction

user_id: References Users collection

recipe_id: References Recipes collection

type: Interaction type (view, like, cook)

rating: Numeric rating (only for cook interactions, 1–5)

timestamp: Interaction timestamp

Example:

{
  "interaction_id": "I0001",
  "user_id": "U003",
  "recipe_id": "R016",
  "type": "view",
  "rating": null,
  "timestamp": "2025-11-20T06:05:00Z"
}


Schema Image:


2. Pipeline Instructions

Follow these steps to set up and run the pipeline.

Step 1: Install Dependencies
pip install firebase-admin pandas

Step 2: Set Up Firebase

Create a Firebase project on Firebase Console
.

Enable Firestore Database in the project.

Download the service account key JSON file.

Place serviceAccountKey.json in the project root directory.

Step 3: Upload Data (Task 2)

Run the main ETL script:

python main.py


This script does:

Inserts Veg Pulav + 19 synthetic recipes

Adds 5 users

Generates 50 user interactions (views, likes, cooks)

Step 4: Run Validation (Task 3)

Run the validation script:

python task3_output/validate_data.py


Output:

Generates validation_report.json

Lists valid and invalid records

Step 5: Run Analytics (Task 5)

Run the analytics module:

python task3_output/analytics.py


Insights Produced:

Most common ingredients across all recipes

Average preparation and cook time

Difficulty distribution (Easy, Medium, Hard)

Correlation between prep time and likes

Most frequently viewed recipes

Ingredients associated with high engagement

Average rating of recipes cooked by users

Users with highest interactions

Recipes with highest total interactions

Cuisine popularity based on engagement

Charts can also be generated if your script includes Matplotlib or Plotly visualizations.

3. ETL Process Overview
3.1 Extract

Reads raw JSON files:

recipes.json – all recipes

users.json – all users

user_interactions.json – all interactions

Loads data into Python objects or Pandas DataFrames for processing.

3.2 Transform

Schema Validation:

Required fields exist (recipe_id, user_id, ingredients)

Field types are correct (numeric for qty_numeric, integer for times)

Ratings exist only for cook interactions

Steps are correctly ordered

Data Cleaning:

Missing qty_numeric → set as null

Null ratings for non-cook interactions allowed

Units and numeric quantities standardized

Standardization:

Normalize fields like rating and qty_numeric for analytics

Ensure uniform format for recipes, users, and interactions

3.3 Load

Uploads data to Firestore:

Recipes Collection

Users Collection

UserInteractions Collection

Ensures clean, structured, and query-ready data.

4. Analytics & Insights (Task 5)

The analytics module provides 10 key insights:

Most Common Ingredients Across Recipes

Average Preparation and Cook Times

Difficulty Distribution of Recipes (Easy, Medium, Hard)

Correlation Between Prep Time and Number of Likes

Most Frequently Viewed Recipes

Ingredients Associated with High Engagement

Average Rating of Recipes Cooked by Users

Users with Highest Interactions

Recipes with Highest Total Interactions

Cuisine Popularity Based on Engagement Metrics

5. Known Constraints / Limitations

Synthetic Data: JSON files mostly synthetic; may not cover all real-world cases

Rating Field: Exists only for cook interactions

Quantity Fields: qty_numeric optional

Overwriting Firestore Data: Repeated ETL runs may overwrite documents

CSV Dependency: Analytics scripts require CSVs in task3_output

Memory & Performance: Large datasets may need optimization

Limited Users: Only 5 users generated; real-world requires more dynamic users

6. Visualization

Optional: Matplotlib or Plotly for charts

Can visualize:

Ingredient popularity

Recipe difficulty distribution

User interaction trends

7. Future Enhancements

Add more dynamic users and interactions

Support real-time analytics dashboards

Include image upload for recipes

Integrate recommendation system