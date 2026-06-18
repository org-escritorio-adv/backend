import unicodedata

import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src import config
from src.shared.permissoes import efetivas
from src.usuarios.model import Usuario as UsuarioModel

KEYCLOAK_URL = config.KEYCLOAK_SERVER_URL
REALM_NAME = config.KEYCLOAK_REALM
ADMIN_CLIENT_ID = config.KEYCLOAK_ADMIN_CLIENT_ID
ADMIN_CLIENT_SECRET = config.KEYCLOAK_ADMIN_CLIENT_SECRET


def _obter_token_admin():
    url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": ADMIN_CLIENT_ID,
        "client_secret": ADMIN_CLIENT_SECRET,
    }
    response = requests.post(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro de autenticação interna com o Keycloak")
    return response.json().get("access_token")


def _normalize_perfil(perfil: str) -> str:
    """Normaliza "Admin"/"Advogado"/"Estagiário" → "admin"/"advogado"/"estagiario"."""
    s = unicodedata.normalize("NFKD", perfil).encode("ASCII", "ignore").decode("ASCII").lower()
    mapping = {"admin": "admin", "advogado": "advogado", "estagiario": "estagiario"}
    return mapping.get(s, "advogado")


def _atribuir_role_keycloak(token: str, keycloak_id: str, role_name: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    role_resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/roles/{role_name}",
        headers=headers,
    )
    if role_resp.status_code != 200:
        return
    requests.post(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{keycloak_id}/role-mappings/realm",
        json=[role_resp.json()],
        headers={**headers, "Content-Type": "application/json"},
    )


def _to_dict(usuario: UsuarioModel) -> dict:
    nome = usuario.nome or ""
    iniciais = "".join(p[0].upper() for p in nome.split() if p)[:2] or "US"
    return {
        "id": usuario.keycloak_id or str(usuario.id),
        "nome": nome,
        "email": usuario.email,
        "perfil": usuario.perfil,
        "telefone": usuario.telefone,
        "oab": usuario.oab,
        "status": "Ativo",
        "avatar": iniciais,
        "permissoes": efetivas(usuario.perfil, usuario.permissoes),
        "created_at": usuario.created_at,
        "updated_at": usuario.updated_at,
    }


def _extract_perfil_from_roles(roles: list[str]) -> str:
    roles_lower = [r.lower() for r in roles]
    if "admin" in roles_lower:
        return "admin"
    if "advogado" in roles_lower:
        return "advogado"
    if "estagiario" in roles_lower:
        return "estagiario"
    return "advogado"


# ── CRUD ──────────────────────────────────────────────────────────────────────


def _deletar_usuario_keycloak(token: str, keycloak_id: str) -> None:
    """Deleta usuário no Keycloak; ignora erros (usado apenas em rollback compensatório)."""
    try:
        requests.delete(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{keycloak_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
    except Exception:
        pass


def criar(db: Session, dados):
    token = _obter_token_admin()

    # 1. Cria no Keycloak
    response = requests.post(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users",
        json={
            "username": dados.email,
            "email": dados.email,
            "firstName": dados.nome,
            "enabled": True,
            "emailVerified": True,
            "credentials": [{"type": "password", "value": dados.senha, "temporary": False}],
        },
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    if response.status_code != 201:
        raise HTTPException(status_code=400, detail=f"Erro ao criar usuário no Keycloak: {response.text}")

    location = response.headers.get("Location", "")
    keycloak_id = location.split("/")[-1] if location else None
    if not keycloak_id:
        raise HTTPException(status_code=500, detail="Keycloak não retornou o ID do usuário criado")

    # 2. Atribui a role no Keycloak
    perfil_local = _normalize_perfil(getattr(dados, "perfil", "advogado") or "advogado")
    _atribuir_role_keycloak(token, keycloak_id, perfil_local)

    # 3. Salva no banco local; se falhar, desfaz a criação no Keycloak (compensação)
    db_usuario = UsuarioModel(
        keycloak_id=keycloak_id,
        nome=dados.nome,
        email=dados.email,
        senha_hash="keycloak",
        perfil=perfil_local,
    )
    try:
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
    except Exception as exc:
        db.rollback()
        _deletar_usuario_keycloak(token, keycloak_id)
        raise HTTPException(status_code=500, detail="Erro ao salvar usuário no banco de dados.") from exc

    return _to_dict(db_usuario)


def listar(db: Session):
    """
    Fonte principal: Keycloak (lista todos os usuários do realm).
    Enriquece com dados locais (telefone, oab, perfil correto) quando disponíveis.
    """
    try:
        token = _obter_token_admin()
        response = requests.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code != 200:
            raise ValueError("Keycloak indisponível")
        kc_users = response.json()
    except Exception:
        # Fallback: retorna apenas os usuários locais
        return [_to_dict(u) for u in db.query(UsuarioModel).all()]

    # Mapa keycloak_id → registro local (evita N+1)
    local_map: dict[str, UsuarioModel] = {
        u.keycloak_id: u
        for u in db.query(UsuarioModel).all()
        if u.keycloak_id
    }

    result = []
    for kc_user in kc_users:
        kc_id = kc_user.get("id")
        kc_nome = (
            f"{kc_user.get('firstName', '')} {kc_user.get('lastName', '')}".strip()
            or kc_user.get("username", "")
        )
        local = local_map.get(kc_id)
        nome = local.nome if local else kc_nome
        iniciais = "".join(p[0].upper() for p in nome.split() if p)[:2] or "US"
        perfil = local.perfil if local else ("admin" if kc_user.get("username") == "admin" else "advogado")

        result.append({
            "id": kc_id,
            "nome": nome,
            "email": local.email if local else kc_user.get("email", ""),
            "perfil": perfil,
            "telefone": local.telefone if local else None,
            "oab": local.oab if local else None,
            "status": "Ativo" if kc_user.get("enabled") else "Inativo",
            "avatar": iniciais,
            "permissoes": efetivas(perfil, local.permissoes if local else None),
            "created_at": local.created_at if local else None,
            "updated_at": local.updated_at if local else None,
        })
    return result


def buscar_por_id(db: Session, item_id: str):
    local = db.query(UsuarioModel).filter(UsuarioModel.keycloak_id == item_id).first()
    if local:
        return _to_dict(local)
    return None


def buscar_por_keycloak_id(db: Session, keycloak_id: str) -> UsuarioModel | None:
    return db.query(UsuarioModel).filter(UsuarioModel.keycloak_id == keycloak_id).first()


def sincronizar_do_keycloak(db: Session) -> None:
    """Startup: provisiona no banco qualquer usuário que já existe no Keycloak."""
    try:
        token = _obter_token_admin()
        response = requests.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code != 200:
            return

        existing_ids = {
            u.keycloak_id
            for u in db.query(UsuarioModel).all()
            if u.keycloak_id
        }

        for kc_user in response.json():
            kc_id = kc_user.get("id")
            if not kc_id or kc_id in existing_ids:
                continue

            roles_resp = requests.get(
                f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{kc_id}/role-mappings/realm",
                headers={"Authorization": f"Bearer {token}"},
            )
            roles = (
                [r.get("name", "") for r in roles_resp.json()]
                if roles_resp.status_code == 200
                else []
            )

            nome = (
                f"{kc_user.get('firstName', '')} {kc_user.get('lastName', '')}".strip()
                or kc_user.get("username", "Usuário")
            )
            email = kc_user.get("email") or kc_user.get("username", "")
            provisionar_ou_buscar(db, kc_id, email, nome, roles)

    except Exception:
        pass  # Não bloqueia o startup se o Keycloak ainda não estiver disponível


def provisionar_ou_buscar(db: Session, keycloak_id: str, email: str, preferred_username: str, roles: list[str]) -> UsuarioModel:
    """Auto-provisiona um registro local na primeira vez que o usuário acessa /me."""
    local = db.query(UsuarioModel).filter(UsuarioModel.keycloak_id == keycloak_id).first()
    if local:
        return local
    perfil = _extract_perfil_from_roles(roles)
    local = UsuarioModel(
        keycloak_id=keycloak_id,
        nome=preferred_username,
        email=email,
        senha_hash="keycloak",
        perfil=perfil,
    )
    db.add(local)
    db.commit()
    db.refresh(local)
    return local


def atualizar(db: Session, item_id: str, dados):
    local = db.query(UsuarioModel).filter(UsuarioModel.keycloak_id == item_id).first()
    if not local:
        return None

    if getattr(dados, "nome", None) is not None:
        local.nome = dados.nome
    if getattr(dados, "email", None) is not None:
        local.email = dados.email
    if getattr(dados, "telefone", None) is not None:
        local.telefone = dados.telefone
    if getattr(dados, "oab", None) is not None:
        local.oab = dados.oab
    if getattr(dados, "perfil", None) is not None:
        local.perfil = _normalize_perfil(dados.perfil)

    novo_email = getattr(dados, "email", None)

    # Mudança de e-mail é bloqueante: Keycloak é a fonte de autenticação,
    # divergência quebraria o login do usuário.
    if novo_email:
        try:
            token = _obter_token_admin()
            resp = requests.put(
                f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{item_id}",
                json={"email": novo_email, "username": novo_email},
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            )
            if resp.status_code not in (200, 204):
                db.rollback()
                raise HTTPException(status_code=502, detail="Falha ao atualizar e-mail no Keycloak.")
        except HTTPException:
            raise
        except Exception as exc:
            db.rollback()
            raise HTTPException(status_code=502, detail="Não foi possível contactar o Keycloak.") from exc

    db.commit()
    db.refresh(local)

    # Demais campos (nome) propagados de forma não-bloqueante
    nome_novo = getattr(dados, "nome", None)
    if nome_novo:
        try:
            token = _obter_token_admin()
            requests.put(
                f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{item_id}",
                json={"firstName": nome_novo},
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            )
        except Exception:
            pass

    return _to_dict(local)


def atualizar_permissoes(db: Session, item_id: str, permissoes: dict[str, bool]):
    """Salva o override individual de permissões de um usuário (admin)."""
    local = db.query(UsuarioModel).filter(UsuarioModel.keycloak_id == item_id).first()
    if not local:
        return None

    local.permissoes = permissoes
    db.commit()
    db.refresh(local)
    return _to_dict(local)


def remover(db: Session, item_id: str) -> bool:
    local = db.query(UsuarioModel).filter(UsuarioModel.keycloak_id == item_id).first()
    if not local:
        return False

    from src.notificacoes.model import Notificacao
    from src.processos.model import Processo
    from src.tarefas.model import Tarefa

    vinculos = []
    if db.query(Processo.id).filter(Processo.advogado_id == local.id).first():
        vinculos.append("processos")
    if db.query(Tarefa.id).filter(Tarefa.responsavel_id == local.id).first():
        vinculos.append("tarefas")

    if vinculos:
        raise HTTPException(
            status_code=409,
            detail=(
                "Usuário não pode ser removido enquanto estiver vinculado a "
                f"{', '.join(vinculos)}. Reatribua esses registros antes de remover."
            ),
        )

    token = _obter_token_admin()

    try:
        db.query(Notificacao).filter(Notificacao.usuario_id == local.id).update(
            {Notificacao.usuario_id: None},
            synchronize_session=False,
        )
        db.delete(local)
        db.flush()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao remover usuário no banco de dados.") from exc

    # Só remove no Keycloak depois que o banco aceitou a remoção local.
    # Se o Keycloak falhar, o rollback preserva o registro local.
    try:
        resp = requests.delete(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{item_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code not in (200, 204, 404):
            raise HTTPException(
                status_code=502,
                detail=f"Falha ao remover usuário do Keycloak (status {resp.status_code}).",
            )
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail="Não foi possível contactar o Keycloak.") from exc

    db.commit()
    return True
