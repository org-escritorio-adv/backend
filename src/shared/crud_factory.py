from collections.abc import Callable
from typing import Any, List, Type

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.keycloak_auth import require_roles, require_roles_or_permission


def create_crud_router(
    prefix: str,
    tags: List[str],
    model: Type[BaseModel],
    model_create: Type[BaseModel],
    model_update: Type[BaseModel],
    listar: Callable[[Session], list[Any]],
    buscar_por_id: Callable[[Session, int], Any | None],
    criar: Callable[[Session, BaseModel], Any],
    atualizar: Callable[[Session, int, BaseModel], Any | None],
    remover: Callable[[Session, int], bool],
    resource_name: str = "Recurso",
    roles_listar: list[str] | None = None,
    roles_buscar: list[str] | None = None,
    roles_criar: list[str] | None = None,
    roles_atualizar: list[str] | None = None,
    roles_remover: list[str] | None = None,
    # Permissão individual (chave do dict `permissoes` do usuário) que, se
    # ativa, libera acesso mesmo para quem não tem nenhuma das roles acima.
    permissao_listar: str | None = None,
    permissao_buscar: str | None = None,
    permissao_criar: str | None = None,
    permissao_atualizar: str | None = None,
    permissao_remover: str | None = None,
) -> APIRouter:

    router = APIRouter(prefix=prefix, tags=tags)

    # ── helpers ──────────────────────────────────────────────────────────
    def _role_deps(roles: list[str] | None, permissao: str | None = None) -> list:
        """Retorna lista de dependencies para proteger a rota, se roles ou
        permissão individual foram informadas."""
        if roles is None and permissao is None:
            return []
        if permissao is None:
            return [Depends(require_roles(*roles))]
        return [Depends(require_roles_or_permission(roles, permissao))]

    # ── GET / ────────────────────────────────────────────────────────────
    @router.get(
        "/", response_model=List[model], dependencies=_role_deps(roles_listar, permissao_listar)
    )
    def list_items(db: Session = Depends(get_db)):
        return listar(db)

    # ── GET /{id} ────────────────────────────────────────────────────────
    @router.get(
        "/{item_id}",
        response_model=model,
        dependencies=_role_deps(roles_buscar, permissao_buscar),
    )
    def get_item(item_id: str, db: Session = Depends(get_db)):
        item = buscar_por_id(db, item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"{resource_name} não encontrado!")
        return item

    # ── POST / ───────────────────────────────────────────────────────────
    @router.post(
        "/",
        response_model=model,
        status_code=201,
        dependencies=_role_deps(roles_criar, permissao_criar),
    )
    def create_item(body: model_create, db: Session = Depends(get_db)):
        return criar(db, body)

    # ── PATCH /{id} ──────────────────────────────────────────────────────
    @router.patch(
        "/{item_id}",
        response_model=model,
        dependencies=_role_deps(roles_atualizar, permissao_atualizar),
    )
    def update_item(item_id: str, body: model_update, db: Session = Depends(get_db)):
        item = atualizar(db, item_id, body)
        if not item:
            raise HTTPException(status_code=404, detail=f"{resource_name} não encontrado!")
        return item

    # ── DELETE /{id} ─────────────────────────────────────────────────────
    @router.delete(
        "/{item_id}",
        status_code=204,
        dependencies=_role_deps(roles_remover, permissao_remover),
    )
    def delete_item(item_id: str, db: Session = Depends(get_db)):
        sucesso = remover(db, item_id)
        if not sucesso:
            raise HTTPException(status_code=404, detail=f"{resource_name} não encontrado!")

    return router