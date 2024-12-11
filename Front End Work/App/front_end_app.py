from flask import Flask, render_template, request
import requests

app = Flask(__name__)


# Home page/search/admin button
@app.route("/")
def home():
    return render_template("search.html")


# Recipe search route
@app.route("/search",  methods=["POST"])

def search_recipe():
    form_data = request.form.getlist('ingredient-tag')
    
    query = ",".join(form_data)
    print(query)

    url = f"http://127.0.0.1:8000/query/{query}"
    response = requests.post(url)

    if response.status_code == 200:
        data = response.json()
        recipes = [
        {
            "label" : hit.get("recipe", {}).get("label"),
            "image": hit.get("recipe", {}).get("image"),
            "url": hit.get("recipe", {}).get("url"),
            "source": hit.get("recipe", {}).get("source"),
        }
        for hit in data.get("hits", [])
        ]
        print(recipes)
    else:
        data = {"results": []}
        print("-----NO RESPONSE FROM API-----")

    return render_template("search_results.html", recipes=recipes, query=query)


# Recipe Details Route
@app.route("/recipes/<key>/<id>")
def recipe_details(key, id):
    print(key)
    print(id)

    url = f"http://127.0.0.1:8000/query/{key}"
    response = requests.post(url)

    if response.status_code == 200:
        data = response.json()
        recipes = [
        {
            "label" : hit.get("recipe", {}).get("label"),
            "ingredientLines": hit.get("recipe", {}).get("ingredientLines", []),
            "image": hit.get("recipe", {}).get("image"),
            "url": hit.get("recipe", {}).get("url"),
            "source": hit.get("recipe", {}).get("source"),
            "calories": int(hit.get("recipe", {}).get("calories")),
            "url": hit.get("recipe", {}).get("url"),
        }
        for hit in data.get("hits", [])
        ]

        recipe = recipes[int(id) - 1]
        print(recipe)

        return render_template("history_and_details.html", recipe=recipe) 
    else:
        data = {"results": []}
        print("-----NO RESPONSE FROM API-----")


    return render_template("history_and_details.html" )


# returns stats dashboard
@app.route("/dash")
def dashboard():
    return render_template("dash.html")


if __name__ == "__main__":
    app.run(port=3000, debug=True)
