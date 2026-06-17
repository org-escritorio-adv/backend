from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.keycloak_auth import get_current_user, require_roles_or_permission
from src.shared.crud_factory import create_crud_router
from src.usuarios import repository
from src.usuarios.schema import (
    PermissoesUpdate,
    Usuario,
    UsuarioCreate,
    UsuarioMeUpdate,
    UsuarioUpdate,
)

# ── Rotas /me ─────────────────────────────────────────────────────────────────
# Devem ser registradas ANTES do CRUD com /{item_id} para evitar conflito de rota.

_me_router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@_me_router.get("/me", response_model=Usuario)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    keycloak_id = current_user["sub"]
    local = repository.provisionar_ou_buscar(
        db,
        keycloak_id=keycloak_id,
        email=current_user.get("email", ""),
        preferred_username=current_user.get("preferred_username", "Usuário"),
        roles=current_user.get("realm_roles", []),
    )
    return repository._to_dict(local)


@_me_router.patch("/me", response_model=Usuario)
async def update_me(
    body: UsuarioMeUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    keycloak_id = current_user["sub"]
    # Garante que o registro local existe antes de atualizar
    repository.provisionar_ou_buscar(
        db,
        keycloak_id=keycloak_id,
        email=current_user.get("email", ""),
        preferred_username=current_user.get("preferred_username", "Usuário"),
        roles=current_user.get("realm_roles", []),
    )
    updated = repository.atualizar(db, keycloak_id, body)
    if not updated:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")
    return updated


# ── Rota de permissões individuais ───────────────────────────────────────────

_permissoes_router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@_permissoes_router.patch(
    "/{item_id}/permissoes",
    response_model=Usuario,
    dependencies=[Depends(require_roles_or_permission(["admin"], "gerenciarUsuarios"))],
)
async def atualizar_permissoes(
    item_id: str,
    body: PermissoesUpdate,
    db: Session = Depends(get_db),
):
    item = repository.atualizar_permissoes(db, item_id, body.permissoes)
    if not item:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return item


# ── CRUD router ────────────────────────────────────────────────────────────────

_crud_router = create_crud_router(
    prefix="/usuarios",
    tags=["usuarios"],
    model=Usuario,
    model_create=UsuarioCreate,
    model_update=UsuarioUpdate,
    listar=repository.listar,
    buscar_por_id=repository.buscar_por_id,
    criar=repository.criar,
    atualizar=repository.atualizar,
    remover=repository.remover,
    resource_name="Usuário",
    roles_listar=["admin", "advogado", "estagiario"],
    roles_buscar=["admin"],
    roles_criar=["admin"],
    roles_atualizar=["admin"],
    roles_remover=["admin"],
)

# Router combinado — /me e /{item_id}/permissoes antes de /{item_id}
router = APIRouter()
router.include_router(_me_router)
router.include_router(_permissoes_router)
router.include_router(_crud_router)
