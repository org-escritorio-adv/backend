import base64
import io
import csv
import os
import uuid
from datetime import datetime
from fpdf import FPDF
from fastapi import Depends, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.keycloak_auth import require_roles, require_roles_or_permission
from src.processos import repository
from src.processos.schema import Processo, ProcessoCreate, ProcessoUpdate, DocumentoProcessoSchema
from src.processos.model import DocumentoProcesso
from src.shared.crud_factory import create_crud_router

from fastapi import APIRouter

DOCS_UPLOAD_DIR = "uploads/documentos_processo"
if os.getenv("VERCEL") == "1":
    DOCS_UPLOAD_DIR = "/tmp/escritorio-adv/documentos_processo"
DOCS_UPLOAD_DIR = os.getenv("DOCUMENTOS_UPLOAD_DIR", DOCS_UPLOAD_DIR)

EXTENSOES_PERMITIDAS = {".pdf", ".jpg", ".jpeg", ".png", ".docx", ".doc", ".xlsx", ".xls"}
TAMANHO_MAXIMO = 20 * 1024 * 1024  # 20 MB


class DocumentoUploadRequest(BaseModel):
    arquivo_base64: str
    arquivo_nome: str

router = APIRouter(prefix="/processos", tags=["processos"])

crud_router = create_crud_router(
    prefix="",
    tags=["processos"],
    model=Processo,
    model_create=ProcessoCreate,
    model_update=ProcessoUpdate,
    listar=repository.listar,
    buscar_por_id=repository.buscar_por_id,
    criar=repository.criar,
    atualizar=repository.atualizar,
    remover=repository.remover,
    resource_name="Processo",
    roles_listar=["admin", "advogado", "estagiario"],
    roles_buscar=["admin", "advogado", "estagiario"],
    roles_criar=["admin", "advogado"],
    roles_atualizar=["admin", "advogado"],
    roles_remover=["admin", "advogado"],
    # Permite que um estagiário com a permissão individual correspondente
    # ativada no Painel de Permissões também tenha acesso, sem precisar
    # ter a role "advogado"/"admin".
    permissao_criar="criarProcessos",
    permissao_atualizar="editarProcessos",
    permissao_remover="excluirProcessos",
)


@router.patch(
    "/{processo_id}/favoritar",
    response_model=Processo,
    dependencies=[Depends(require_roles("admin", "advogado", "estagiario"))],
)
def favoritar_processo(processo_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException

    item = repository.toggle_favorite(db, processo_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado!")
    return item


@router.get(
    "/exportar-csv",
    dependencies=[Depends(require_roles_or_permission(["admin", "advogado"], "exportarDados"))],
)
def exportar_csv(db: Session = Depends(get_db)):
    processos = repository.listar(db)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Número CNJ", "Tribunal", "Partes", "Status", "Favorito"])
    
    for p in processos:
        writer.writerow([p.id, p.numero_cnj, p.tribunal, p.partes, p.status, p.favorito])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=processos.csv"}
    )


@router.get(
    "/{processo_id}/exportar-pdf",
    dependencies=[Depends(require_roles("admin", "advogado", "estagiario"))],
)
def exportar_pdf(processo_id: int, db: Session = Depends(get_db)):
    processo = repository.buscar_por_id(db, processo_id)
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
        
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="Relatório de Processo", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Número CNJ: {processo.numero_cnj}", ln=True)
    pdf.cell(200, 10, txt=f"Tribunal: {processo.tribunal or 'N/A'}", ln=True)
    pdf.cell(200, 10, txt=f"Status: {processo.status}", ln=True)
    
    pdf.ln(10)
    pdf.cell(200, 10, txt="Últimas Movimentações:", ln=True)
    movimentacoes = sorted(processo.movimentacoes, key=lambda m: m.data, reverse=True)[:3]
    for mov in movimentacoes:
        pdf.cell(200, 10, txt=f"- {mov.data.strftime('%d/%m/%Y') if mov.data else ''}: {mov.descricao[:100]}", ln=True)
        
    out = pdf.output()
    pdf_bytes = bytes(out) if isinstance(out, bytearray) else out.encode('latin-1', errors='replace')
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=processo_{processo.numero_cnj}.pdf"}
    )

@router.get(
    "/{processo_id}/documentos",
    response_model=list[DocumentoProcessoSchema],
    dependencies=[Depends(require_roles("admin", "advogado", "estagiario"))],
)
def listar_documentos(processo_id: int, db: Session = Depends(get_db)):
    docs = db.query(DocumentoProcesso).filter(DocumentoProcesso.processo_id == processo_id).all()
    return docs


@router.post(
    "/{processo_id}/documentos",
    response_model=DocumentoProcessoSchema,
    dependencies=[Depends(require_roles("admin", "advogado"))],
)
def upload_documento(processo_id: int, body: DocumentoUploadRequest, db: Session = Depends(get_db)):
    processo = repository.buscar_por_id(db, processo_id)
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")

    ext = os.path.splitext(body.arquivo_nome)[1].lower()
    if ext not in EXTENSOES_PERMITIDAS:
        raise HTTPException(status_code=422, detail=f"Formato não permitido. Use: {', '.join(EXTENSOES_PERMITIDAS)}")

    try:
        conteudo = base64.b64decode(body.arquivo_base64)
    except Exception:
        raise HTTPException(status_code=422, detail="Arquivo base64 inválido.")

    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(status_code=422, detail="Arquivo excede 20 MB.")

    os.makedirs(DOCS_UPLOAD_DIR, exist_ok=True)
    nome_salvo = f"{processo_id}_{uuid.uuid4().hex}{ext}"
    with open(os.path.join(DOCS_UPLOAD_DIR, nome_salvo), "wb") as f:
        f.write(conteudo)

    doc = DocumentoProcesso(
        processo_id=processo_id,
        nome_original=body.arquivo_nome,
        nome_salvo=nome_salvo,
        tamanho=len(conteudo),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get(
    "/{processo_id}/documentos/{doc_id}/arquivo",
    dependencies=[Depends(require_roles("admin", "advogado", "estagiario"))],
)
def baixar_documento(processo_id: int, doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(DocumentoProcesso).filter(
        DocumentoProcesso.id == doc_id,
        DocumentoProcesso.processo_id == processo_id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    caminho = os.path.join(DOCS_UPLOAD_DIR, doc.nome_salvo)
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no servidor")

    return FileResponse(caminho, filename=doc.nome_original)


@router.delete(
    "/{processo_id}/documentos/{doc_id}",
    dependencies=[Depends(require_roles("admin", "advogado"))],
    status_code=204,
)
def remover_documento(processo_id: int, doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(DocumentoProcesso).filter(
        DocumentoProcesso.id == doc_id,
        DocumentoProcesso.processo_id == processo_id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    caminho = os.path.join(DOCS_UPLOAD_DIR, doc.nome_salvo)
    if os.path.exists(caminho):
        os.remove(caminho)

    db.delete(doc)
    db.commit()


router.include_router(crud_router)

