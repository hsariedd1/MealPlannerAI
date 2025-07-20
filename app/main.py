from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ✅ Using your project-scoped key and project ID
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    project="proj_GtvTRNh4PBFyjS4vQLDeGIQW"
)

app = FastAPI()

class UserProfile(BaseModel):
    age: int
    gender: str
    height: str
    weight: int
    body_fat: Optional[float] = None
    dietary_preferences: str
    weekly_budget: int
    zipcode: str
    fitness_goal: str

@app.post("/meal-plan")
def generate_meal_plan(profile: UserProfile):
    prompt = f"""
You are a certified sports nutritionist and personal meal planning assistant.

Generate a complete weekly meal plan and grocery list for the following user:

- Age: {profile.age}
- Gender: {profile.gender}
- Height: {profile.height}
- Weight: {profile.weight} lbs
- Body fat %: {profile.body_fat if profile.body_fat else 'Not provided'}
- Fitness goal: {profile.fitness_goal}
- Dietary preference: {profile.dietary_preferences}
- Weekly grocery budget: ${profile.weekly_budget}
- Zip code: {profile.zipcode}

Instructions:

1. Create a 7-day meal plan. Each day should include:
   - 3 meals (breakfast, lunch, dinner)
   - 1 snack
   - Focus on high-protein, nutrient-dense foods
   - Include lean meats, seafood, legumes, and high-protein grains
   - Rotate ingredients to minimize cost and food waste
   - Keep prep time reasonable (ideally under 30 minutes)

2. For each meal:
   - Provide a descriptive name
   - List ingredients with quantities and units
   - Include basic cooking instructions
   - Include estimated prep + cook time

3. Generate a grocery list based on the entire week's plan:
   - Item name
   - Quantity and unit
   - Category
   - Estimated price (based on stores near zip code {profile.zipcode})
   - Group by category
   - Keep total estimated grocery cost under ${profile.weekly_budget}

4. Assume local stores like Walmart, Kroger, Aldi, or Target. Avoid exotic or hard-to-find items.

5. At the very end of your response, after the grocery list, include a JSON block labeled MACROS with the following format:

MACROS:
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

6. Do not include anything else after the JSON. Make sure the JSON is valid.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful nutrition assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        return {"meal_plan": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
