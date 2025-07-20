from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import openai
import os
from dotenv import load_dotenv

# ✅ Load environment variables locally (no effect on Render if already set)
load_dotenv()

# ✅ Set your OpenAI API key (Render must have OPENAI_API_KEY set)
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# -------------------------------
# Request models
# -------------------------------

class MealPlanRequest(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[int] = None
    body_fat: Optional[float] = None
    dietary_preferences: Optional[str] = None
    weekly_budget: Optional[int] = None
    zipcode: Optional[str] = None
    fitness_goal: Optional[str] = None

class CustomizeRequest(BaseModel):
    original_plan: str
    customization: str

# -------------------------------
# Endpoints
# -------------------------------

@app.post("/meal-plan")
async def meal_plan(req: MealPlanRequest):
    prompt = f"""
Create a 7-day meal plan for:
Age: {req.age}
Gender: {req.gender}
Height: {req.height}
Weight: {req.weight}
Body Fat %: {req.body_fat}
Dietary Preferences: {req.dietary_preferences}
Weekly Budget: {req.weekly_budget}
Zipcode: {req.zipcode}
Fitness Goal: {req.fitness_goal}

Assume local stores like Walmart, Kroger, Aldi, or Target. Avoid exotic or hard-to-find items.

Format your response in **Markdown** with clear headings:
- Weekly Meal Plan (Day-by-day)
- Recipes
- Grocery List (Grouped)
- Total Estimated Grocery Cost

At the very end, include a JSON block labeled MACROS with:
{{
  "average_calories": <average daily calories>,
  "average_protein_g": <average daily protein grams>,
  "average_carbs_g": <average daily carbs grams>,
  "average_fats_g": <average daily fats grams>,
  "sample_meals_day1": [
    "Breakfast: <short name>",
    "Lunch: <short name>",
    "Dinner: <short name>",
    "Snack: <short name>"
  ]
}}
Do not include anything else after the JSON. Make sure the JSON is valid.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful nutrition assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        return {"meal_plan": response["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"error": str(e)}

@app.post("/customize")
async def customize_plan(req: CustomizeRequest):
    prompt = f"""
The following is an existing 7-day meal plan with grocery list and MACROS at the end:
---
{req.original_plan}
---
Now regenerate this plan using these customization instructions:
"{req.customization}"

Your response must include:
✅ A full updated 7-day meal plan
✅ A section titled 'GROCERY LIST:' with all updated items
✅ A section titled 'MACROS:' with updated JSON
Return everything as plain text.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful nutrition assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        return {"meal_plan": response["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"error": str(e)}
