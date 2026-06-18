import os

from fastapi import Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.advogados import repository
from src.advogados.schema import Advogado, AdvogadoCreate, AdvogadoUpdate
from src.database import get_db
from src.keycloak_auth import require_roles
from src.shared import storage
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/advogados",
    tags=["Advogados"],
    model=Advogado,
    model_create=AdvogadoCreate,
    model_update=AdvogadoUpdate,
    listar=repository.listar_advogados,
    buscar_por_id=repository.buscar_advogado,
    criar=repository.criar_advogado,
    atualizar=repository.atualizar_advogado,
    remover=repository.remover_advogado,
    resource_name="Advogado",
    # Lista pública: a landing page institucional exibe a equipe para
    # visitantes anônimos, portanto o GET / não exige autenticação.
    roles_listar=None,
    roles_buscar=None,
    roles_criar=["admin"],
    roles_atualizar=["admin"],
    roles_remover=["admin"],
)


# ── Upload da foto do advogado (Cloudflare R2) ──────────────────────────────
EXTENSOES_IMAGEM = {".jpg", ".jpeg", ".png", ".webp"}
CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
TAMANHO_MAXIMO = 5 * 1024 * 1024  # 5 MB


@router.post(
    "/{advogado_id}/foto",
    response_model=Advogado,
    dependencies=[Depends(require_roles("admin"))],
    summary="Faz upload da foto do advogado para o Cloudflare R2",
)
def upload_foto(
    advogado_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    advogado = repository.buscar_advogado(db, advogado_id)
    if not advogado:
        raise HTTPException(status_code=404, detail="Advogado não encontrado!")

    if not storage.r2_configurado():
        raise HTTPException(
            status_code=503,
            detail="Armazenamento de imagens (R2) não configurado no servidor.",
        )

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in EXTENSOES_IMAGEM:
        raise HTTPException(
            status_code=422,
            detail=f"Formato não permitido. Use: {', '.join(sorted(EXTENSOES_IMAGEM))}",
        )

    conteudo = file.file.read()
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(status_code=422, detail="Imagem excede 5 MB.")

    content_type = file.content_type if file.content_type in CONTENT_TYPES else "image/jpeg"

    foto_antiga = advogado.foto_url
    nova_url = storage.upload_imagem(
        conteudo,
        content_type=content_type,
        prefixo=f"advogados/{advogado_id}",
        extensao=ext,
    )

    advogado.foto_url = nova_url
    db.commit()
    db.refresh(advogado)

    # Remove a imagem anterior do bucket (best-effort)
    storage.remover_por_url(foto_antiga)

    return advogado
