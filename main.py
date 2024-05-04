import requests
from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = '12345'

def search_recipes(ingredients, num_results=5):
    api_endpoint = "https://api.edamam.com/search"
    app_id = "API_ID"
    app_key = "API_KEY"
    
    params = {
        "q": ",".join(ingredients),
        "app_id": app_id,
        "app_key": app_key,
        "from": 0,
        "to": num_results
    }
    
    try:
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        
        recipes = []
        if 'hits' in data and data['hits']:
            for hit in data['hits']:
                recipe = hit['recipe']
                nutrition_info = recipe['totalNutrients']
                relevant_nutrients = {}
                for nutrient in ['ENERC_KCAL', 'FAT', 'SUGAR', 'CHOCDF', 'PROCNT']:
                    if nutrient in nutrition_info:
                        relevant_nutrients[nutrient] = round(nutrition_info[nutrient]['quantity'], 2)
                    else:
                        relevant_nutrients[nutrient] = 0
                recipes.append({
                    'label': recipe['label'],
                    'url': recipe['url'],
                    'image': recipe['image'],
                    'ingredients': recipe['ingredientLines'],
                    'nutrition_info': relevant_nutrients
                })
            
        return recipes
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ingredients = request.form.get('ingredients')
        num_recipes = request.form.get('num_recipes')

        if ingredients and num_recipes:
            ingredients_list = ingredients.split(',')
            try:
                num_recipes = int(num_recipes)
                if num_recipes <= 0:
                    raise ValueError("Number of recipes must be a positive integer.")
            except ValueError as ve:
                return render_template('index.html', error=f"Invalid input: {ve}")

            recipes = search_recipes(ingredients_list, num_results=num_recipes)

            if recipes:
                session['recipes'] = recipes
                return render_template('index.html', recipe=recipes[0], show_another_button=True)
            else:
                return render_template('index.html', error="No recipes found.")
        
    return render_template('index.html')

@app.route('/another_recipe', methods=['GET',"POST"])
def another_recipe():
    recipes = session.get('recipes')
    if recipes:
        if len(recipes) > 1:
            session['recipes'] = recipes[1:]
            return render_template('index.html', recipe=recipes[1], show_another_button=True)
    
    if request.method == 'POST':
        ingredients = request.form.get('ingredients')
        num_recipes = request.form.get('num_recipes')

        if ingredients and num_recipes:
            ingredients_list = ingredients.split(',')
            try:
                num_recipes = int(num_recipes)
                if num_recipes <= 0:
                    raise ValueError("Number of recipes must be a positive integer.")
            except ValueError as ve:
                return render_template('index.html', error=f"Invalid input: {ve}")

            recipes = search_recipes(ingredients_list, num_results=num_recipes)

            if recipes:
                session['recipes'] = recipes
                return render_template('index.html', recipe=recipes[0], show_another_button=True)
            else:
                return render_template('index.html', error="No recipes found.")

    return render_template('index.html', show_another_button=False)

if __name__ == '__main__':
    app.run(debug=True)


