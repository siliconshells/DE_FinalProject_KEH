import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
from back_end import (
    app,
    get_a_secret,
    get_ingredients,
    search_recipes,
    save_user_activity,
)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("back_end.get_db_connection")
@patch("back_end.prompt")
def test_get_ingredients(mock_prompt, mock_get_db_connection):
    mock_prompt.return_value = "Short history of ingredients."
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn

    ingredients = "tomato, basil"
    result = get_ingredients(ingredients)

    assert "ingredient_histories" in result
    assert result["ingredient_histories"] == "Short history of ingredients."
    assert "recipes" in result

    mock_conn.cursor.assert_called()
    mock_conn.close.assert_called()


@patch("back_end.requests.get")
def test_search_recipes(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"hits": ["recipe1", "recipe2"]}
    mock_get.return_value = mock_response

    query = "tomato, basil"
    recipes = search_recipes(query)

    assert recipes == {"hits": ["recipe1", "recipe2"]}
    mock_get.assert_called_with(
        "https://api.edamam.com/search",
        params={
            "q": query,
            "app_id": get_a_secret("EDAMAM_APP_ID"),
            "app_key": get_a_secret("EDAMAM_APP_KEY"),
            "to": 10,
        },
    )


@patch("back_end.psycopg2.connect")
def test_save_user_activity(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    save_user_activity(mock_conn, datetime.now(), "tomato, basil", "test_user")

    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called()
    mock_cursor.close.assert_called()


@patch("back_end.get_db_connection")
def test_report(mock_get_db_connection, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_conn

    mock_cursor.fetchall.return_value = [
        ("2024-12-12 12:00:00", "test_ingredient", "test_user")
    ]

    response = client.get("/report/busiest_day")
    assert response.status_code == 200
    mock_cursor.execute.assert_called()
    mock_conn.close.assert_called()
