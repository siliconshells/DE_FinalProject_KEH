from flask import Flask, render_template, request
import requests

app = Flask(__name__)


# Home page/search/admin button
@app.route("/")
def home():
    return render_template("search.html")


# Recipe search route
@app.route("/search", methods=["POST"])
def search_recipe():
    query = request.form["query"]
   
    url = f"https://openlibrary.org/search.json?q={query}" #put new URL here
    response = requests.get(url)
    data = response.json()

    recipes = [
        {
            "Name": recipe.get("[recipe name]"), #change this based on url
            "Ingredients": ", ".join(recipe.get("ingredients", [])),
            "cover_i": recipe.get("cover_i"),
            "key": recipe.get("key"),
        }
        for recipe in data.get("docs", [])
    ]

    return render_template("search_results.html", recipes=recipes, query=query)


# Recipe Details Route
@app.route("/recipes/<key>")
def book_details(key):
    url = f"https://openlibrary.org/works/{key}.json" #change out url here
    response = requests.get(url)
    recipe = response.json()

    details = {
        "Name": recipe.get("title"),
        "Ingredients": recipe.get("description", {}),
        "Directions": recipe.get("directions", []),
        "cover_image": recipe.get("covers", [None])[0],
    }

    return render_template("history_and_details.html", details=details)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run( port=3000, debug=True)