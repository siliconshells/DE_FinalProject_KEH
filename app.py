from flask import Flask, jsonify
from flask.logging import create_logger
import logging
import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)
LOG = create_logger(app)
LOG.setLevel(logging.INFO)

# This is a temporary app to test CICD and IaC


@app.route("/")
def home():
    html = f"<h3>Hi I am Flask.  I come to conquer-via Continuous Delivery</h3>"
    return html.format(format)


@app.route("/hi/<name>")
def hello(name):
    greeting = f"Hello: {name}"
    return jsonify(greeting)


@app.route("/test_database")
def test_database():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        return "Connection successful"
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()


# if __name__ == "__main__":
#     # app.run(host="127.0.0.1", port=8081, debug=True)
#     app.run(host="0.0.0.0", port=5006, debug=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
