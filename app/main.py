from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import os
from dotenv import load_dotenv

# ✅ Load environment variables (useful for local dev)
load_dotenv()

# ✅ Initialize OpenAI client with your project ID
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    project="proj_GtvTRNh4PBFyjS4vQLDeGIQW"
)

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
# Helper: prompt suffix with MACROS instructions
# -------------------------------
MACROS_INSTRUCTIONS = """
IMPORTANT:
At the very end of your response, add a new section that starts with the exact header `MACROS:` followed by a valid JSON block with these keys:
- average_calories (integer)
- average_protein_g (integer)
- average_carbs_g (integer)
- average_fats_g (integer)
- sample_meals_day1 (an array of exactly 4 short strings for Breakfast, Lunch, Dinner, Snack)

Example format:

MACROS:
{
  "average_calories": 2100,
  "average_protein_g": 180,
  "average_carbs_g": 200,
  "average_fats_g": 60,
  "sample_meals_day1": [
    "Breakfast: Greek yogurt with almonds",
    "Lunch: Grilled chicken salad",
    "Dinner: Lean turkey pasta",
    "Snack: Protein shake with banana"
  ]
}

⚠️ Do not put anything after this JSON block. Make sure the JSON is valid and parsable.
"""

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

Include clear Markdown sections:
- Weekly Meal Plan (Day-by-day)
- Recipes
- Grocery List (Grouped)
- Total Estimated Grocery Cost

{MACROS_INSTRUCTIONS}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful nutrition assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        return {"meal_plan": response.choices[0].message.content}
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

{MACROS_INSTRUCTIONS}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful nutrition assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        return {"meal_plan": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
