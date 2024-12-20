from flask import Flask, render_template, request
from back_end import get_ingredients, report

app = Flask(__name__)


# Home page/search/admin button
@app.route("/")
def home():
    return render_template("search.html")


# Recipe search route
@app.route("/search", methods=["POST"])
def search_recipe():
    form_data = request.form.getlist("ingredient-tag")

    query = ",".join(form_data)
    print(query)

    data = get_ingredients(query)
    if data:
        recipes = [
            {
                "label": hit.get("recipe", {}).get("label"),
                "image": hit.get("recipe", {}).get("image"),
                "url": hit.get("recipe", {}).get("url"),
                "source": hit.get("recipe", {}).get("source"),
            }
            for hit in data.get("recipes", {}).get("hits", [])
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

    data = get_ingredients(key)

    if data:

        recipes = [
            {
                "label": hit.get("recipe", {}).get("label"),
                "ingredientLines": hit.get("recipe", {}).get("ingredientLines", []),
                "image": hit.get("recipe", {}).get("image"),
                "source": hit.get("recipe", {}).get("source"),
                "calories": int(hit.get("recipe", {}).get("calories")),
                "url": hit.get("recipe", {}).get("url"),
            }
            for hit in data.get("recipes", {}).get("hits", [])
        ]
        llm_response = [
            {
                "text": text.get("text", {}),
            }
            for text in data.get("ingredient_histories", {}).get("content", [])
        ]

        print(llm_response, "this is the llm response")

        recipe = recipes[int(id) - 1]
        # print(recipe)

        return render_template(
            "history_and_details.html", recipe=recipe, llm_response=llm_response
        )
    else:
        data = {"results": []}
        print("-----NO RESPONSE FROM API-----")

    return render_template("history_and_details.html")


# returns stats dashboard
@app.route("/dash")
def dashboard():
    return render_template("dash.html")


@app.route("/health")
def health_check():
    return {"status": "healthy"}, 200


@app.route("/report/<type_of_report>")
def get_report(type_of_report):
    return report(type_of_report)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
