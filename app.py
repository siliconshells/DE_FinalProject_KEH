from flask import Flask, request, render_template
import requests

app = Flask(__name__)

# Replace these with your Edamam credentials
EDAMAM_APP_ID = "304ebfbb"
EDAMAM_APP_KEY = "c83cfb887e89e36b1ef366d4eeddd571"
EDAMAM_API_URL = "https://api.edamam.com/search"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            return search_recipes(query)
    return render_template('index.html')

def search_recipes(query):
    params = {
        'q': query,
        'app_id': EDAMAM_APP_ID,
        'app_key': EDAMAM_APP_KEY,
        'to': 10  # Limit results to 10
    }
    response = requests.get(EDAMAM_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return render_template('results.html', recipes=data.get('hits', []))
    else:
        return f"Error: {response.status_code} - {response.reason}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)