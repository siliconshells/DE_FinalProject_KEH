from flask import Flask, jsonify

# from flask.logging import create_logger
# import logging
import psycopg2
import json
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

load_dotenv()


app = Flask(__name__)
# LOG = create_logger(app)
# LOG.setLevel(logging.INFO)

# This is a temporary app to test CICD and IaC


@app.route("/")
def home():
    html = f"<h3>Hi I am Flask.  I come to conquer-via Continuous Delivery</h3>"
    return html.format(format)


@app.route("/hi/<name>")
def hello(name):
    greeting = f"Hello: {name}"
    return jsonify(greeting)


def get_secrets():

    secret_name = "flask_app_secrets"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    return get_secret_value_response


@app.route("/test_database")
def test_database():
    conn = None
    secrets = get_secrets()
    try:
        secrets = json.loads(secrets["SecretString"])
        # print(secrets["SecretString"]["DB_HOST"])

        conn = psycopg2.connect(
            host=secrets["DB_HOST"],
            port=5432,
            user=secrets["DB_USER"],
            password=secrets["DB_PASSWORD"],
        )
        return "Connection successful"
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()


# if __name__ == "__main__":
#     # app.run(host="127.0.0.1", port=8081, debug=True)
#     app.run(host="0.0.0.0", port=5006, debug=True)
@app.route("/health")
def health_check():
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
