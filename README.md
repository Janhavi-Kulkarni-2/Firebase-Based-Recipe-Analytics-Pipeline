# Firebase-Based Recipe Analytics Pipeline

This project is a complete **recipe management and analytics pipeline** using **Firebase Firestore**, Python, and Pandas.  
It allows you to:

- Add recipes, users, and interactions  
- Validate the data  
- Perform analytics  
- Generate insights with a clean ETL process  

---

## Table of Contents

1. [Data Model](#data-model)  
2. [Pipeline Instructions](#pipeline-instructions)  
3. [ETL Process Overview](#etl-process-overview)  
4. [Analytics & Insights](#analytics--insights)  
5. [Visualization](#visualization)  
6. [Known Limitations](#known-limitations)  
7. [Future Enhancements](#future-enhancements)  

---

## 1. Data Model

The data model efficiently captures **recipes, users, and interactions** for analytics, validation, and ETL processing.

### A. Recipes Collection

Stores details of each recipe. Each recipe has a **unique `recipe_id`**.

**Fields:**

- `name`: Name of the recipe  
- `description`: Short description  
- `servings`: Number of servings  
- `prep_time_minutes` & `cook_time_minutes`: Cooking times  
- `difficulty`: Difficulty level (Easy, Medium, Hard)  
- `cuisine`: Cuisine type (e.g., Indian, Italian, Chinese)  
- `ingredients`: Array of objects (`name`, `qty_numeric`, `unit`, `qty_text`)  
- `steps`: Array of objects (`step_order`, `step_text`)  
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
Schema Image:


B. Users Collection
Stores information about registered users.

Fields:

user_id: Unique identifier

name: User’s name

email: User’s email

joined_at: Timestamp

Example:

json
Copy code
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
Schema Image:


2. Pipeline Instructions
Follow these step-by-step instructions to set up and run the project.

Step 1: Install Dependencies
bash
Copy code
pip install firebase-admin pandas
Step 2: Set Up Firebase
Create a Firebase project at Firebase Console

Enable Firestore database in the project

Download the service account key JSON file

Place serviceAccountKey.json in the project root directory

Step 3: Upload Data (Task 2)
Run the main ETL script:

bash
Copy code
python main.py
What this does:

Inserts Veg Pulav + 19 synthetic recipes

Adds 5 users

Generates 50 user interactions (views, likes, cooks)

Step 4: Run Validation (Task 3)
Run the validation script:

bash
Copy code
python task3_output/validate_data.py
Output:

Generates validation_report.json

Lists valid and invalid records

Step 5: Run Analytics (Task 5)
Run the analytics module:

bash
Copy code
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

3. ETL Process Overview
The ETL (Extract, Transform, Load) process cleans, validates, and loads recipe data from JSON files into Firestore.

3.1 Extract
Reads JSON files: recipes.json, users.json, user_interactions.json

Loads them into Python objects or Pandas DataFrames

DataFrames allow easy filtering, manipulation, and analysis

3.2 Transform
Schema Validation
Required fields present (recipe_id, user_id, ingredients)

Field types consistent (qty_numeric numeric, prep_time_minutes integer)

Ratings only for cook interactions

Steps are correctly ordered

Data Cleaning
qty_numeric missing → set as null

Null ratings allowed for non-cook interactions

Units and numeric quantities standardized

Standardization
Normalize rating and qty_numeric

Ensures uniform format for analytics

3.3 Load
Uploads data into Firestore collections:

Recipes

Users

UserInteractions

Data ready for querying, analytics, and visualization

4. Analytics & Insights
Provides 10 key insights:

Most common ingredients across recipes

Average preparation and cook times

Difficulty distribution (Easy, Medium, Hard)

Correlation between prep time and likes

Most frequently viewed recipes

Ingredients associated with high engagement

Average rating of recipes cooked by users

Users with highest interactions

Recipes with highest total interactions

Cuisine popularity based on engagement

5. Known Limitations
Synthetic Data: Mostly synthetic for testing

Rating Field Limitations: Only for cook interactions

Quantity Fields Optional: qty_numeric may be missing

Overwriting Firestore Data: ETL runs may overwrite documents

Dependency on CSVs: Required in task3_output

Memory & Performance: Large datasets may need optimization

Limited User Base: Only 5 users; real-world projects require more

6. Visualization
Use Matplotlib or Plotly to generate charts for:

Ingredient popularity

Recipe difficulty distribution

Prep time vs likes correlation

User engagement metrics

7. Future Enhancements
Add real user data instead of synthetic data

Support dynamic recipe addition via web interface

Implement recommendation engine for personalized recipes

Add advanced analytics dashboards

