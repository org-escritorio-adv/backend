def create_processo_helper(client):
    payload = {
        "numero_cnj": "0001234-56.2023.8.26.0000",
        "tribunal": "TJSP",
        "partes": "Autor vs Réu",
        "favorito": True
    }
    response = client.post("/processos/", json=payload)
    return response.json()

def test_create_processo(client):
    data = create_processo_helper(client)
    assert data["numero_cnj"] == "0001234-56.2023.8.26.0000"
    assert "id" in data

def test_list_processos(client):
    create_processo_helper(client)
    response = client.get("/processos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["numero_cnj"] == "0001234-56.2023.8.26.0000"

def test_update_processo(client):
    novo_processo = create_processo_helper(client)
    processo_id = novo_processo["id"]
    
    payload = {"status": "arquivado"}
    response = client.patch(f"/processos/{processo_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "arquivado"

def test_delete_processo(client):
    novo_processo = create_processo_helper(client)
    processo_id = novo_processo["id"]
    
    response = client.delete(f"/processos/{processo_id}")
    assert response.status_code == 204
    
    # Verifica se foi deletado
    get_response = client.get(f"/processos/{processo_id}")
    assert get_response.status_code == 404
