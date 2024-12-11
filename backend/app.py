
import requests
import psycopg2
import os
import google.generativeai as genai
import json
from flask import Flask, request, render_template
from datetime import datetime
from dotenv import load_dotenv
import boto3



load_dotenv()

app = Flask(__name__)

# Edamam credentials
EDAMAM_APP_ID = os.getenv('EDAMAM_APP_ID')
EDAMAM_APP_KEY = os.getenv('EDAMAM_APP_KEY')
EDAMAM_API_URL = os.getenv('EDAMAM_API_URL')

# PostgreSQL connection details
DB_CONFIG = {
    "host": os.getenv('DBHOST'),
    "user": os.getenv('DBUSER'),
    "password": os.getenv('DBPASSWORD'),
    "port": os.getenv('DBPORT'),
}

# Amazon LLM Connection Credientials
AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID"),
AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
BEDROCK_MODEL_ID=os.getenv("BEDROCK_MODEL_ID")

client = boto3.client("bedrock-runtime", region_name="us-west-2")
def prompt(llm_input):

    prompt = llm_input

    # Format the request payload for the LLM
    native_request = {
        "modelId": "anthropic.claude-3-5-haiku-20241022-v1:0",
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 200,
                "top_k": 250,
                "temperature": 0,
                "top_p": 0.999,
                "messages": [{"role": "user", "content": prompt}],
            }
        ),
    }

    try:
        response = client.invoke_model(**native_request)
        model_response = json.loads(response["body"].read())
        return model_response
    except Exception as e:
        raise Exception(f"Error: {e}")
    

# Establish database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print("Error connecting to database:", e)
        return None


# Function to save user activity
def save_user_activity(conn, activity_time, ingredients, username):
    try:
        cursor = conn.cursor()
        ingredients = ingredients.lower()
        query = """
            INSERT INTO user_activity (activity_time, ingredients, username)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (activity_time, ingredients, username))
        conn.commit()
        print("Data saved successfully")
    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()


@app.route("/query/<ingredients>", methods=["GET", "POST"])
def index(ingredients):
    if ingredients:
        conn = get_db_connection()
        if conn:
            try:
                # Save user activity to the database
                activity_time = datetime.now()
                username = "guest_user"  # Replace with actual username if available
                save_user_activity(
                    conn, activity_time, ingredients, username
                )
            finally:
                conn.close()

        # Query Bedrock for ingredient histories
        ingredient_histories = prompt(f"Please return a short history of the following ingredients: {ingredients}")

        # Search for recipes using Edamam API
        recipes = search_recipes(ingredients)

        # Combine and return results
        return {
            "ingredient_histories": ingredient_histories,
            "recipes": recipes
        }


def search_recipes(query):
    """Searches recipes from the Edamam API."""
    params = {
        "q": query,
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_APP_KEY,
        "to": 10,  # Limit results to 10
    }
    response = requests.get(EDAMAM_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return f"Error: {response.status_code} - {response.reason}"


@app.route("/report/<type_of_report>")
def report(type_of_report):
    """Displays a report of user queries."""
    conn = get_db_connection()
    if conn:
        try:
            query_string = ("SELECT * FROM user_activity ORDER BY activity_time DESC")
            if type_of_report == "busiest_day": 
                query_string = """SELECT activity_time, COUNT(*) AS occurrence_count
                                FROM user_activity
                                GROUP BY activity_time
                                ORDER BY occurrence_count DESC
                                LIMIT 1;"""
            elif type_of_report == "top_search":
                query_string = """SELECT ingredient, COUNT(*) AS occurrence_count
                                FROM (SELECT unnest(string_to_array(ingredients, ',')) AS ingredient
                                FROM user_activity) AS ingredient_list
                                GROUP BY ingredient
                                ORDER BY occurrence_count DESC
                                LIMIT 10"""
            cursor = conn.cursor()
            cursor.execute(query_string)
            user_activities = cursor.fetchall()
            return user_activities
        except Exception as e:
            return f"Error retrieving user activity: {e}"
        finally:
            conn.close()
    else:
        return "Error: Could not connect to the database."



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
