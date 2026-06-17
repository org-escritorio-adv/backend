import pytest
from src.advogados.model import Advogado

def create_advogado_helper(client):
    payload = {
        "nome": "Dr. Joao Teste",
        "cargo": "Sócio",
        "especialidade": "Tributário",
        "oab": "12345/SP",
        "email": "joao@teste.com",
        "bio": "Bio de teste"
    }
    response = client.post("/advogados/", json=payload)
    return response

def test_create_advogado(client):
    response = create_advogado_helper(client)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Dr. Joao Teste"
    assert data["cargo"] == "Sócio"

def test_list_advogados(client):
    # Cria primeiro
    create_advogado_helper(client)
    response = client.get("/advogados/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(adv["nome"] == "Dr. Joao Teste" for adv in data)

def test_get_advogado(client):
    res_create = create_advogado_helper(client)
    adv_id = res_create.json()["id"]

    response = client.get(f"/advogados/{adv_id}")
    assert response.status_code == 200
    assert response.json()["id"] == adv_id

def test_update_advogado(client):
    res_create = create_advogado_helper(client)
    adv_id = res_create.json()["id"]

    payload = {
        "cargo": "Sócio Sênior"
    }
    response = client.patch(f"/advogados/{adv_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["cargo"] == "Sócio Sênior"

def test_delete_advogado(client):
    res_create = create_advogado_helper(client)
    adv_id = res_create.json()["id"]

    response = client.delete(f"/advogados/{adv_id}")
    assert response.status_code == 204

    response_get = client.get(f"/advogados/{adv_id}")
    assert response_get.status_code == 404
