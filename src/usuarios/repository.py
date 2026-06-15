import unicodedata
import requests
from fastapi import HTTPException
from src import config

KEYCLOAK_URL = config.KEYCLOAK_SERVER_URL
REALM_NAME = config.KEYCLOAK_REALM
ADMIN_CLIENT_ID = config.KEYCLOAK_ADMIN_CLIENT_ID
ADMIN_CLIENT_SECRET = config.KEYCLOAK_ADMIN_CLIENT_SECRET

# Mapeamento perfil (frontend) → nome da role no Keycloak
_ROLE_KEYCLOAK = {"admin": "Admin", "advogado": "Advogado", "estagiario": "Estagiario"}

# Mapeamento nome da role no Keycloak → label de exibição
_ROLE_DISPLAY = {"Admin": "Admin", "Advogado": "Advogado", "Estagiario": "Estagiário"}


def _normalizar(s: str) -> str:
    """Remove acentos e converte para minúsculas para comparação case-insensitive."""
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()


def obter_token_admin_backend() -> str:
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

def _buscar_perfil_usuario(user_id: str, headers: dict) -> str:
    """Busca as realm roles reais do usuário no Keycloak."""
    resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}/role-mappings/realm",
        headers=headers,
    )
    if resp.status_code == 200:
        for role in resp.json():
            name = role.get("name", "")
            if name in _ROLE_DISPLAY:
                return _ROLE_DISPLAY[name]
    return "Advogado"


def _formatar_usuario(user: dict, headers: dict) -> dict:
    user_id = user.get("id", "")
    nome = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip() or user.get("username", "")
    avatar = "".join(p[0] for p in nome.split()[:2]).upper() or "US"
    return {
        "id": user_id,
        "nome": nome,
        "email": user.get("email", ""),
        "telefone": "",
        "perfil": _buscar_perfil_usuario(user_id, headers),
        "status": "Ativo" if user.get("enabled") else "Inativo",
        "avatar": avatar,
        "permissoes": {},
    }

def listar(db=None):
    token = obter_token_admin_backend()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users", headers=headers)
    if response.status_code != 200:
        return []
    return [_formatar_usuario(u, headers) for u in response.json()]


def buscar_por_id(db=None, item_id: str = None):
    if not item_id:
        return None
    token = obter_token_admin_backend()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{item_id}", headers=headers)
    if response.status_code != 200:
        return None
    return _formatar_usuario(response.json(), headers)


def criar(db, dados):
    token = obter_token_admin_backend()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    partes = dados.nome.strip().split(" ", 1)
    first_name = partes[0]
    last_name = partes[1] if len(partes) > 1 else partes[0]

    response = requests.post(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users",
        json={
            "username": dados.email,
            "email": dados.email,
            "firstName": first_name,
            "lastName": last_name,
            "enabled": True,
            "emailVerified": True,
            "credentials": [{"type": "password", "value": dados.senha, "temporary": False}],
        },
        headers=headers,
    )

    if response.status_code == 409:
        raise HTTPException(status_code=409, detail="Já existe um usuário com este e-mail.")
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=400, detail=f"Erro ao criar usuário no Keycloak: {response.text}")

    location = response.headers.get("Location", "")
    user_id = location.rstrip("/").split("/")[-1] if location else ""

    if not user_id:
        raise HTTPException(status_code=500, detail="Keycloak não retornou o Location com o ID")

    keycloak_role = _ROLE_KEYCLOAK.get(_normalizar(dados.perfil), "Advogado")
    role_resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/roles/{keycloak_role}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if role_resp.status_code == 200:
        requests.post(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}/role-mappings/realm",
            json=[role_resp.json()],
            headers=headers,
        )

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
