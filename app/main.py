from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# ✅ GPT client setup
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    project="proj_GtvTRNh4PBFyjS4vQLDeGIQW"
)

# ✅ Original request model for meal-plan
class MealPlanRequest(BaseModel):
    age: int | None = None
    gender: str | None = None
    height: str | None = None
    weight: int | None = None
    body_fat: float | None = None
    dietary_preferences: str | None = None
    weekly_budget: int | None = None
    zipcode: str | None = None
    fitness_goal: str | None = None

# ✅ New request model for customization
class CustomizeRequest(BaseModel):
    original_plan: str
    customization: str

# ------------------------------------------------------------
# ✅ Existing endpoint: generate a new meal plan
# ------------------------------------------------------------
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

Include:
✅ A section titled 'GROCERY LIST:' with all needed items.
✅ A section titled 'MACROS:' with JSON containing:
  average_calories, average_protein_g, average_carbs_g, average_fats_g, and sample_meals_day1.
Return everything as plain text.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    plan = response.choices[0].message.content
    return {"meal_plan": plan}


# ------------------------------------------------------------
# ✅ New endpoint: customize an existing plan
# ------------------------------------------------------------
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

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    new_plan = response.choices[0].message.content
    return {"meal_plan": new_plan}
