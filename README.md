# Firebase-Based Recipe Analytics Pipeline

This project is a complete **recipe management and analytics pipeline** using **Firebase Firestore**, Python, and Pandas. It allows you to add recipes, users, and interactions, validate the data, perform analytics, and generate insights with a clean ETL process.

## Table of Contents
1. [Data Model](#data-model)
2. [Pipeline Instructions](#pipeline-instructions)
3. [ETL Process Overview](#etl-process-overview)
4. [Analytics & Insights](#analytics--insights)
5. [Visualization](#visualization)
6. [Known Limitations](#known-limitations)
7. [Future Enhancements](#future-enhancements)




---

## 1. Explanation of the Data Model

The data model is designed to efficiently capture **recipes, users, and interactions** for analytics, validation, and ETL processing.

### A. Recipes Collection
Stores details of each recipe. Each recipe has a **unique `recipe_id`** (Primary Key).

**Fields:**
- `name`: Name of the recipe  
- `description`: Short description  
- `servings`: Number of servings  
- `prep_time_minutes` & `cook_time_minutes`: Cooking times  
- `difficulty`: Difficulty level (Easy, Medium, Hard)  
- `cuisine`: Cuisine type (e.g., Indian, Italian, Chinese)  
- `ingredients`: Array of objects (`name`, `qty_numeric`, `unit`, `qty_text`)  
- `steps`: Array of strings (ordered cooking steps)  
- `created_at`: Timestamp  

**Example:**
```json
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

![alt text](schema1.png)


B. Users Collection
Stores information about registered users.

Fields:

- user_id: Unique identifier

- name: User’s name

- email: User’s email

- joined_at: Timestamp

Example:

json
Copy code
{
  "user_id": "U001",
  "name": "Janhavi",
  "email": "janhavi@example.com",
  "joined_at": "2025-11-20T06:00:00Z"
}

![alt text](schema-2.png)

C. UserInteractions Collection
Records how users interact with recipes.

Fields:

- interaction_id: Unique ID for interaction

- user_id: References Users collection

- recipe_id: References Recipes collection

- type: Interaction type (view, like, cook)

- rating: Numeric rating (only for cook interactions, 1–5)

- timestamp: Interaction timestamp

Example:

json
Copy code
{
  "interaction_id": "I0001",
  "user_id": "U003",
  "recipe_id": "R016",
  "type": "view",
  "rating": null,
  "timestamp": "2025-11-20T06:05:00Z"
}

![alt text](schema3.png)

2. Instructions for Running the Pipeline
Follow these step-by-step instructions to set up and run the project.

Step 1: Install Dependencies
Install the required Python packages : pip install firebase-admin pandas

Step 2: Set Up Firebase
Create a Firebase project at Firebase Console.
Enable Firestore database in the project.
Download the service account key JSON file.
Place serviceAccountKey.json in the project root directory.

Step 3: Upload Data (Task 2)
Run the main ETL script:
python main.py

What this does:
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

Insights Produced

The analytics module generates the following insights:

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


3. ETL Process Overview

The ETL (Extract, Transform, Load) process cleans, validates, and loads recipe data from JSON files into Firestore for analytics and querying.

3.1 Extract

The pipeline first reads the raw JSON files:

recipes.json – contains all recipes (Veg Pulav + synthetic recipes)

users.json – contains all user records

user_interactions.json – contains interactions (view, like, cook)

These JSON files are loaded into Python objects and/or Pandas DataFrames.

Using DataFrames allows easy manipulation, filtering, and analysis.

This step ensures all data is loaded into memory in a structured form ready for transformation.

3.2 Transform

Schema Validation:

The pipeline checks:

Required fields are present (e.g., recipe_id, user_id, ingredients)

Field types are consistent (e.g., numeric values for qty_numeric, integers for prep_time_minutes)

Ratings are only present for cook interactions; other types (view/like) must have null

Steps are correctly ordered and formatted

Data Cleaning:

Missing or inconsistent values are handled as follows:

If qty_numeric is missing, it is set as null

Null ratings for non-cook interactions are allowed

Units and numeric quantities are standardized for consistent analytics

Standardization:

Fields like rating and qty_numeric are normalized to ensure calculations in analytics are accurate

Ensures recipes, users, and interactions are in a uniform format before insertion

3.3 Load

After validation and cleaning, the pipeline uploads data into Firestore:

Recipes collection: stores all recipe documents

Users collection: stores all user documents

UserInteractions collection: stores all interaction documents

The loaded data is now ready for querying, analytics, and visualization.

4. Insights Summary (Task 5)

The analytics module provides 10 key insights:

Most Common Ingredients Across Recipes
Identifies which ingredients appear most frequently across all recipes

Average Preparation and Cook Times
Calculates mean prep and cook times for all recipes

Difficulty Distribution of Recipes
Counts recipes per difficulty level (Easy, Medium, Hard)

Correlation Between Prep Time and Number of Likes
Analyzes whether longer or shorter prep times influence user likes

Most Frequently Viewed Recipes
Finds recipes with the highest number of view interactions

Ingredients Associated with High Engagement
Finds ingredients that appear in recipes with the most likes or cooks

Average Rating of Recipes Cooked by Users
Computes mean rating for recipes cooked by users

Users with Highest Interactions
Identifies the most active users by counting total interactions

Recipes with Highest Total Interactions
Counts total interactions per recipe

Cuisine Popularity Based on Engagement Metrics
Analyzes which cuisines have the highest engagement

5. Known Constraints / Limitations

Synthetic Data: JSON files are mostly synthetic for testing purposes and may not cover all real-world scenarios

Rating Field Limitations: Ratings exist only for cook interactions

Quantity Fields Optional: qty_numeric in ingredients is optional

Overwriting Firestore Data: Repeated ETL runs may overwrite existing documents

Dependency on CSVs for Analytics: Analytics scripts require CSVs in task3_output

Memory & Performance Considerations: Large datasets may need optimization


Limited User Base: Only 5 users are generated; real-world usage requires more dynamic users

