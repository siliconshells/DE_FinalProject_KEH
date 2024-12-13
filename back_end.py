import requests
import psycopg2
import json
from flask import Flask
from datetime import datetime
from dotenv import load_dotenv
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
secrets = None
testing = False


def get_secrets():

    # Create a Secrets Manager client
    client = boto3.client(
        "secretsmanager",
        region_name="us-east-1",
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId="flask_app_secrets"
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    return get_secret_value_response


def get_a_secret(secret):
    global testing
    if testing:
        return os.getenv(secret)

    global secrets
    if secrets is None:
        secrets = get_secrets()
        secrets = json.loads(secrets["SecretString"])
    return secrets[secret]


# Edamam credentials
EDAMAM_APP_ID = get_a_secret("EDAMAM_APP_ID")
EDAMAM_APP_KEY = get_a_secret("EDAMAM_APP_KEY")
EDAMAM_API_URL = get_a_secret("EDAMAM_API_URL")

# PostgreSQL connection details
DB_CONFIG = {
    "host": get_a_secret("DB_HOST"),
    "user": get_a_secret("DB_USER"),
    "password": get_a_secret("DB_PASSWORD"),
    "port": 5432,
}

# Amazon LLM Connection Credientials
# We used Jenny's account for Bedrock hence different key
AWS_ACCESS_KEY_ID = (
    get_a_secret("BEDROCK_AWS_ACCESS_KEY_ID")
    if testing
    else get_a_secret("AWS_ACCESS_KEY_ID")
)
AWS_SECRET_ACCESS_KEY = (
    get_a_secret("BEDROCK_AWS_SECRET_ACCESS_KEY")
    if testing
    else get_a_secret("AWS_SECRET_ACCESS_KEY")
)
BEDROCK_MODEL_ID = get_a_secret("BEDROCK_MODEL_ID")

client = boto3.client(
    aws_access_key_id=get_a_secret("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=get_a_secret("AWS_SECRET_ACCESS_KEY"),
    service_name="bedrock-runtime",
    region_name="us-west-2",
)


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


def get_ingredients(ingredients):
    if ingredients:
        conn = get_db_connection(testing)
        if conn:
            try:
                # Save user activity to the database
                activity_time = datetime.now()
                username = "guest_user"  # Replace with actual username if available
                save_user_activity(conn, activity_time, ingredients, username)
            finally:
                conn.close()

        # Query Bedrock for ingredient histories
        ingredient_histories = prompt(
            f"Please return a short history of the following ingredients, complete the response within 200 tokens: {ingredients}"
        )
        print(ingredient_histories)

        # Search for recipes using Edamam API
        recipes = search_recipes(ingredients)

        # Combine and return results
        return {"ingredient_histories": ingredient_histories, "recipes": recipes}


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
            query_string = "SELECT * FROM user_activity ORDER BY activity_time DESC"
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


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5001)
