import json
import time
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from src.config import DATAJUD_API_KEY, DATAJUD_BASE_URL
from src.movimentacoes.model import Movimentacao
from src.processos.model import Processo

_HEADERS = {
    "Authorization": f"APIKey {DATAJUD_API_KEY}",
    "Content-Type": "application/json",
}

_TRIBUNAIS = {
    "tjdft": "api_publica_tjdft", "tjsp": "api_publica_tjsp",
    "tjrj": "api_publica_tjrj",  "tjmg": "api_publica_tjmg",
    "tjrs": "api_publica_tjrs",  "tjpr": "api_publica_tjpr",
    "tjba": "api_publica_tjba",  "tjpe": "api_publica_tjpe",
    "tjce": "api_publica_tjce",  "tjgo": "api_publica_tjgo",
    "tjam": "api_publica_tjam",  "tjma": "api_publica_tjma",
    "tjmt": "api_publica_tjmt",  "tjms": "api_publica_tjms",
    "tjpa": "api_publica_tjpa",  "tjes": "api_publica_tjes",
    "tjpb": "api_publica_tjpb",  "tjrn": "api_publica_tjrn",
    "tjal": "api_publica_tjal",  "tjpi": "api_publica_tjpi",
    "tjse": "api_publica_tjse",  "tjro": "api_publica_tjro",
    "tjto": "api_publica_tjto",  "tjac": "api_publica_tjac",
    "tjap": "api_publica_tjap",  "tjrr": "api_publica_tjrr",
    "tjsc": "api_publica_tjsc",  "trf1": "api_publica_trf1",
    "trf2": "api_publica_trf2",  "trf3": "api_publica_trf3",
    "trf4": "api_publica_trf4",  "trf5": "api_publica_trf5",
    "trf6": "api_publica_trf6",  "tst": "api_publica_tst",
    "stj": "api_publica_stj",    "stm": "api_publica_stm",
    "tse": "api_publica_tse",    "tjm": "api_publica_tjm",
}


def normalizar_tribunal(tribunal: str) -> str:
    t = tribunal.lower()
    if t in _TRIBUNAIS:
        return _TRIBUNAIS[t]
    if t in _TRIBUNAIS.values():
        return t
    raise ValueError(f"Tribunal '{tribunal}' inválido. Use ex: 'tjdft', 'trf1'.")


# ── HTTP ──────────────────────────────────────────────────────────────────────

def consultar_por_numero(
    numero_processo: str,
    tribunal: str,
    tentativas: int = 2,
    timeout: float = 10,
) -> dict:
    """
    Consulta um processo no DataJud.

    Faz até `tentativas` chamadas com timeout curto (`timeout` segundos cada).
    Isso evita que uma instabilidade pontual de rede (comum numa API pública
    compartilhada) derrube a sincronização inteira — só desiste de verdade se
    todas as tentativas falharem.
    """
    alias = normalizar_tribunal(tribunal)
    url = f"{DATAJUD_BASE_URL}/{alias}/_search"
    body = {"query": {"match": {"numeroProcesso": numero_processo}}}

    ultimo_erro: Exception | None = None
    for tentativa in range(1, tentativas + 1):
        try:
            with httpx.Client(timeout=timeout) as client:
                r = client.post(url, json=body, headers=_HEADERS)
                r.raise_for_status()
                return r.json()
        except Exception as e:
            ultimo_erro = e
            if tentativa < tentativas:
                time.sleep(1)  # pequena pausa antes de tentar de novo

    raise ultimo_erro


def buscar_por_filtro(
    tribunal: str,
    numero_processo: str | None = None,
    cpf: str | None = None,
    oab: str | None = None,
    size: int = 10,
) -> dict:
    """Busca por número de processo, CPF de parte ou número OAB do advogado.

    AVISO: partes.cpfCnpj e partes.advogados.numeroOAB são raramente preenchidos
    pelos tribunais no DataJud. Buscas por CPF ou OAB costumam retornar vazio
    mesmo quando o processo existe — isso é uma limitação da fonte de dados.
    """
    if not any([numero_processo, cpf, oab]):
        raise ValueError("Informe ao menos um filtro: numero_processo, cpf ou oab.")

    alias = normalizar_tribunal(tribunal)
    url = f"{DATAJUD_BASE_URL}/{alias}/_search"

    clauses = []
    if numero_processo:
        clauses.append({"match": {"numeroProcesso": numero_processo}})
    if cpf:
        # campo raramente preenchido pelos tribunais — resultado pode ser vazio
        clauses.append({"match": {"partes.cpfCnpj": cpf}})
    if oab:
        # campo raramente preenchido pelos tribunais — resultado pode ser vazio
        clauses.append({"match": {"partes.advogados.numeroOAB": oab}})

    body = {
        "size": size,
        "query": {"bool": {"should": clauses, "minimum_should_match": 1}},
    }

    with httpx.Client(timeout=30) as client:
        r = client.post(url, json=body, headers=_HEADERS)
        r.raise_for_status()
        return r.json()


def buscar_recentes(tribunal: str, size: int = 10, search_after: list | None = None) -> dict:
    alias = normalizar_tribunal(tribunal)
    url = f"{DATAJUD_BASE_URL}/{alias}/_search"
    body: dict = {
        "size": size,
        "query": {"match_all": {}},
        "sort": [{"dataHoraUltimaAtualizacao": "desc"}],
    }
    if search_after:
        body["search_after"] = search_after
    with httpx.Client(timeout=30) as client:
        r = client.post(url, json=body, headers=_HEADERS)
        r.raise_for_status()
        return r.json()


# ── Conversões DataJud → tipos Python ────────────────────────────────────────

def _parse_data_ajuizamento(valor: str | None) -> datetime | None:
    """DataJud envia "20220414183118" (YYYYMMDDHHMMSS)."""
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y%m%d%H%M%S")
    except ValueError:
        return None


def _parse_data_hora_movimento(valor: str | None) -> datetime | None:
    """DataJud envia "2022-04-14T18:31:19.000Z" (ISO 8601 UTC)."""
    if not valor:
        return None
    try:
        return datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        return None


# ── Persistência no banco ─────────────────────────────────────────────────────

def _source_para_processo(source: dict, cliente_id: int | None, advogado_id: int | None) -> Processo:
    """Mapeia _source do ElasticSearch → model Processo."""
    partes_raw = source.get("partes", [])
    return Processo(
        numero_cnj=source.get("numeroProcesso", ""),
        tribunal=source.get("tribunal"),
        partes=json.dumps(partes_raw, ensure_ascii=False) if partes_raw else None,
        data_abertura=_parse_data_ajuizamento(source.get("dataAjuizamento")),
        status="ativo",                           # DataJud não tem campo de status
        favorito=False,
        cliente_id=cliente_id,
        advogado_id=advogado_id,
    )


def _movimentos_para_movimentacoes(movimentos: list, processo_id: int) -> list[Movimentacao]:
    """Mapeia movimentos DataJud → models Movimentacao."""
    resultado = []
    for mov in movimentos:
        data = _parse_data_hora_movimento(mov.get("dataHora"))
        descricao = mov.get("nome", "").strip()
        if not data or not descricao:
            continue
        resultado.append(Movimentacao(
            data=data,
            descricao=descricao,
            processo_id=processo_id,
        ))
    return resultado


def importar_processo(
    db: Session,
    source: dict,
    cliente_id: int | None = None,
    advogado_id: int | None = None,
) -> Processo:
    """
    Recebe _source de um hit do DataJud, persiste em processos + movimentacoes.
    Se o processo já existe (numero_cnj), apenas adiciona movimentações novas.
    """
    numero = source.get("numeroProcesso", "")
    processo = db.query(Processo).filter(Processo.numero_cnj == numero).first()

    if processo is None:
        processo = _source_para_processo(source, cliente_id, advogado_id)
        db.add(processo)
        db.flush()  # gera processo.id sem fechar transação

    movimentos_raw = source.get("movimentos", [])
    novas_movs = _movimentos_para_movimentacoes(movimentos_raw, processo.id)

    # evita duplicatas: descarta movimentações com mesma data+descricao
    existentes = {
        (m.data, m.descricao)
        for m in db.query(Movimentacao).filter(Movimentacao.processo_id == processo.id).all()
    }
    for mov in novas_movs:
        if (mov.data, mov.descricao) not in existentes:
            db.add(mov)

    db.commit()
    db.refresh(processo)
    return processo