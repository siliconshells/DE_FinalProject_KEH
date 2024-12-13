import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import back_end
import os
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def client():
    back_end.app.config["TESTING"] = True
    with back_end.app.test_client() as client:
        yield client


@patch("back_end.get_db_connection")
@patch("back_end.prompt")
def test_get_ingredients(mock_prompt, mock_get_db_connection):
    mock_prompt.return_value = "Short history of ingredients."
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn

    ingredients = "tomato, basil"
    back_end.testing = True
    result = back_end.get_ingredients(ingredients, testing=True)

    assert "ingredient_histories" in result
    assert result["ingredient_histories"] == "Short history of ingredients."
    assert "recipes" in result

    mock_conn.cursor.assert_called()
    mock_conn.close.assert_called()


@patch("back_end.psycopg2.connect")
def test_save_user_activity(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    back_end.save_user_activity(mock_conn, datetime.now(), "tomato, basil", "test_user")

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

    back_end.testing = True
    response = client.get("/report/busiest_day")
    assert response.status_code == 200
    mock_cursor.execute.assert_called()
    mock_conn.close.assert_called()


if __name__ == "__main__":
    test_report(client)
    test_save_user_activity()
    test_get_ingredients()
