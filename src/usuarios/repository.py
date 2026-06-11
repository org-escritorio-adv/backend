import requests
from fastapi import HTTPException

KEYCLOAK_URL = "http://keycloak:8080"
REALM_NAME = "escritorio-realm"
CLIENT_ID = "backend-client"
CLIENT_SECRET = "gUHc20eRvmYZBKiMUSv0M5qa5A44x7ev"

def obter_token_admin_backend():
    """Gera um token de acesso para o backend gerenciar o Keycloak"""
    url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro de autenticação interna com o Keycloak")
    
    return response.json().get("access_token")

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