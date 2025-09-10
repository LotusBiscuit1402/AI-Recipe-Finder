from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)

with open('recipes.json') as f:
    popular_recipes = json.load(f)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

@app.route('/', methods=['GET', 'POST'])
def index():
    ai_recipe = None
    matched_recipes = []
    selected_recipe = None

    if request.method == 'POST':
        ingredients_input = request.form.get('ingredients', '')
        selected_index = request.form.get('selected_index')

        if selected_index:  
            selected_recipe = popular_recipes[int(selected_index)]
        else:
            ingredients_list = [ing.strip().lower() for ing in ingredients_input.split(',') if ing.strip()]

            for recipe in popular_recipes:
                recipe_ingredients = [ing.lower() for ing in recipe["ingredients"]]
                if all(ing in recipe_ingredients for ing in ingredients_list):
                    matched_recipes.append(recipe)

            if not matched_recipes and ingredients_list:
                try:
                    response = client.chat.completions.create(
                        model="gpt-4.1-mini",
                        messages=[
                            {"role": "user", "content": f"Generate up to 3 popular recipes that use all of the following ingredients, along with this add the calories per serving and the nutritional value: {', '.join(ingredients_list)}. For each recipe, include: - Recipe title - Ingredients list (as <ul><li>...</li></ul>) - Instructions (as <ol><li>...</li></ol>). The response must be valid, minimal HTML only (no code fences, no markdown, no extra explanations). Output should be compact and styled with <h2>, <h3>, <ul>, <ol>, and <li> tags."}
                        ],
                        max_tokens=500,
                        temperature=0.7,
                    )
                    ai_recipe = response.choices[0].message.content

                except Exception as e:
                    ai_recipe = f"Error: {str(e)}"

    return render_template(
        'index.html',
        recipes=popular_recipes,
        ai_recipe=ai_recipe,
        matched_recipes=matched_recipes,
        selected_recipe=selected_recipe
    )

if __name__ == '__main__':
    app.run(debug=True)
