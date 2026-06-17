def create_cliente_helper(client):
    payload = {
        "nome_razao_social": "Cliente Teste Integração",
        "cpf_cnpj": "123.456.789-00",
        "email": "cliente@teste.com"
    }
    response = client.post("/clientes/", json=payload)
    return response.json()

def test_create_cliente(client):
    data = create_cliente_helper(client)
    assert data["nome_razao_social"] == "Cliente Teste Integração"
    assert "id" in data

def test_list_clientes(client):
    create_cliente_helper(client)
    response = client.get("/clientes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["nome_razao_social"] == "Cliente Teste Integração"

def test_get_cliente(client):
    novo_cliente = create_cliente_helper(client)
    cliente_id = novo_cliente["id"]
    
    response = client.get(f"/clientes/{cliente_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == cliente_id

def test_update_cliente(client):
    novo_cliente = create_cliente_helper(client)
    cliente_id = novo_cliente["id"]
    
    payload = {"telefone": "99999-9999"}
    response = client.patch(f"/clientes/{cliente_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["telefone"] == "99999-9999"

def test_delete_cliente(client):
    novo_cliente = create_cliente_helper(client)
    cliente_id = novo_cliente["id"]
    
    response = client.delete(f"/clientes/{cliente_id}")
    assert response.status_code == 204
    
    # Verifica se foi deletado
    get_response = client.get(f"/clientes/{cliente_id}")
    assert get_response.status_code == 404
