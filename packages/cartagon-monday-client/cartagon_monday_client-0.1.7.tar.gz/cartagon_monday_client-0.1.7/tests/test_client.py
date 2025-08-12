import json
import pytest
import responses

from monday_client.client import MondayClient
from monday_client.exceptions import MondayAPIError

API_URL = "https://api.monday.com/v2"
TOKEN = "fake-token"


@pytest.fixture
def client():
    return MondayClient(api_key=TOKEN)


@responses.activate
def test_test_connection_success(client):
    # Simulamos una respuesta válida con { data: { me: {...} } }
    body = {"data": {"me": {"id": "1", "name": "Test", "email": "test@example.com"}}}
    responses.add(responses.POST, API_URL, json=body, status=200)

    assert client.test_connection() is True


@responses.activate
def test_test_connection_failure_on_403(client):
    # Simulamos un 403
    responses.add(responses.POST, API_URL, status=403)

    assert client.test_connection() is False


@responses.activate
def test_get_boards_returns_list(client):
    boards_list = [
        {"id": "1", "name": "Board One"},
        {"id": "2", "name": "Board Two"}
    ]
    body = {"data": {"boards": boards_list}}
    responses.add(responses.POST, API_URL, json=body, status=200)

    result = client.get_boards(limit=2, page=1)
    assert isinstance(result, list)
    assert result == boards_list


@responses.activate
def test_get_all_items_paginates_correctly(client):
    # Primera página con cursor
    first = {
        "data": {
            "boards": [{
                "items_page": {
                    "cursor": "CURSOR_1",
                    "items": [{"id": "a", "name": "Item A"}]
                }
            }]
        }
    }
    # Segunda página sin cursor
    second = {
        "data": {
            "next_items_page": {
                "cursor": None,
                "items": [{"id": "b", "name": "Item B"}]
            }
        }
    }

    # Añadimos las dos respuestas en orden
    responses.add(responses.POST, API_URL, json=first, status=200)
    responses.add(responses.POST, API_URL, json=second, status=200)

    items = client.get_all_items(board_id=123, limit=1)
    assert items == [
        {"id": "a", "name": "Item A"},
        {"id": "b", "name": "Item B"}
    ]


@responses.activate
def test_execute_query_raises_on_graphql_error(client):
    # Simulamos un error GraphQL
    body = {"errors": [{"message": "Something went wrong"}]}
    responses.add(responses.POST, API_URL, json=body, status=200)

    with pytest.raises(MondayAPIError) as ei:
        client.get_boards(limit=1, page=1)
    assert "Something went wrong" in str(ei.value)
