import requests
from fastapi import HTTPException

from src import config

KEYCLOAK_URL = config.KEYCLOAK_SERVER_URL
REALM_NAME = config.KEYCLOAK_REALM
ADMIN_CLIENT_ID = config.KEYCLOAK_ADMIN_CLIENT_ID
ADMIN_CLIENT_SECRET = config.KEYCLOAK_ADMIN_CLIENT_SECRET

def obter_token_admin_backend():
    """Gera um token de acesso para o backend gerenciar o Keycloak"""
    url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": ADMIN_CLIENT_ID,
        "client_secret": ADMIN_CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro de autenticação interna com o Keycloak")
    
    return response.json().get("access_token")

def criar(db, dados):
    token = obter_token_admin_backend()
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "username": dados.email,
        "email": dados.email,
        "firstName": dados.nome,
        "enabled": True,
        "emailVerified": True,
        "credentials": [{
            "type": "password",
            "value": dados.senha,
            "temporary": False
        }]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 201:
        raise HTTPException(status_code=400, detail=f"Erro ao criar usuário no Keycloak: {response.text}")
    
    # Extrai o UUID retornado pelo cabeçalho Location (ex: http://keycloak:8080/admin/realms/escritorio-adv/users/8372b83...)
    location = response.headers.get("Location", "")
    user_id = location.split("/")[-1] if location else None
    
    if not user_id:
        raise HTTPException(status_code=500, detail="Keycloak não retornou o Location com o ID")
        
    return buscar_por_id(db, user_id)

def atualizar(db, item_id, dados):
    token = obter_token_admin_backend()
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{item_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Update fields only if they are provided
    payload = {}
    if getattr(dados, "nome", None):
        payload["firstName"] = dados.nome
    if getattr(dados, "email", None):
        payload["email"] = dados.email
        
    if payload:
        response = requests.put(url, json=payload, headers=headers)
        if response.status_code != 204:
            raise HTTPException(status_code=400, detail=f"Erro ao atualizar usuário no Keycloak: {response.text}")
            
    return buscar_por_id(db, item_id)

def remover(db, item_id):
    token = obter_token_admin_backend()
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(url, headers=headers)
    if response.status_code != 204:
        raise HTTPException(status_code=400, detail=f"Erro ao deletar usuário no Keycloak: {response.text}")
        
    return True

def listar(db=None):
    """Busca os usuários direto do Keycloak em vez do banco de dados local"""
    token = obter_token_admin_backend()
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    
    usuarios_keycloak = response.json()
    lista_formatada = []
    
    for user in usuarios_keycloak:
        username_atual = user.get("username", "usuario_sem_username")
        nome_completo = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
        if not nome_completo or nome_completo == "":
            nome_completo = username_atual

        avatar_iniciais = username_atual[:2].upper() if username_atual else "US"

        lista_formatada.append({
            "id": user.get("id"),
            "nome": nome_completo,
            "email": user.get("email", ""),
            "telefone": "(61) 99999-0000", 
            # 🌟 ALTERADO DE "nivel" PARA "perfil" AQUI:
            "perfil": "Admin" if username_atual == "admin" else "Estagiário", 
            "status": "Ativo" if user.get("enabled") else "Inativo",
            "avatar": avatar_iniciais,
            "permissoes": {}
        })
        
    return lista_formatada

def buscar_por_id(db=None, item_id: str = None):
    """Busca um usuário específico por ID direto no Keycloak"""
    if not item_id:
        return None
        
    token = obter_token_admin_backend()
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
        
    user = response.json()
    
    username_atual = user.get("username", "usuario_sem_username")
    nome_completo = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
    if not nome_completo or nome_completo == "":
        nome_completo = username_atual
        
    avatar_iniciais = username_atual[:2].upper() if username_atual else "US"
    
    return {
        "id": user.get("id"),
        "nome": nome_completo,
        "email": user.get("email", ""),
        "telefone": "(61) 99999-0000",
        # 🌟 ALTERADO DE "nivel" PARA "perfil" AQUI TAMBÉM:
        "perfil": "Admin" if username_atual == "admin" else "Estagiário",
        "status": "Ativo" if user.get("enabled") else "Inativo",
        "avatar": avatar_iniciais,
        "permissoes": {}
    }