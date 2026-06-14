import io
import csv
from fpdf import FPDF
from fastapi import Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.keycloak_auth import require_roles
from src.processos import repository
from src.processos.schema import Processo, ProcessoCreate, ProcessoUpdate
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/processos",
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
    roles_remover=["admin"],
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
    dependencies=[Depends(require_roles("admin", "advogado"))],
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
        
    pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='replace')
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=processo_{processo.numero_cnj}.pdf"}
    )
