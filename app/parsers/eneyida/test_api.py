from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_manifest():
    response = client.get("/watari/manifest.json")
    assert response.status_code == 200


def test_catalog():
    response = client.get("/watari/catalog/series/watari_ТБ-Серіал.json")
    response_data = response.json()

    assert response.status_code == 200
    assert response_data.get("metas") is not None
    assert len(response_data.get("metas")) == 28


def test_catalog_skip():
    response = client.get(
        "/watari/catalog/movie/watari_Повнометражне/skip=56.json"
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data.get("metas") is not None
    assert len(response_data.get("metas")) == 28


def test_series_metadata():
    response = client.get(
        "/watari/meta/series/b26ddd58-f751-4d3c-b17c-a646d60f2b8e.json"
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data.get("meta") is not None
    assert response_data["meta"]["name"] == "Експерименти Лейн"


def test_streams():
    response = client.get(
        "/watari/stream/series/86fcad39-12df-4e1a-8c43-6259a6292ee6/2.json"
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data.get("streams") is not None
    assert len(response_data["streams"]) == 2


def test_search():
    response = client.get(
        "/watari/catalog/series/watari_search/search=Експерименти Лейн.json"
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data.get("metas") is not None
    assert response_data["metas"][0]["name"] == "Експерименти Лейн"
