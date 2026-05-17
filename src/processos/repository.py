from typing import Any

_db: list[dict[str, Any]] = [
    {
        "id": 1,
        "created_at": "2026-04-10",
        "updated_at": "2026-04-10",
        "number": "0001234-56.2023.8.26.0000",
        "court": "TJSP",
        "parts": "João da Silva vs. Empresa Meta",
        "start_date": "2023-05-15",
        "status": "Em andamento",
        "favorite": True,
        "client_id": 1,
        "tribunal_id": 1,
        "advogado_id": 1,
        "movements": [
            {"date": "2023-05-15", "description": "Petição inicial distribuída"},
            {"date": "2023-08-20", "description": "Audiência de conciliação designada"},
        ],
    },
    {
        "id": 2,
        "created_at": "2026-04-11",
        "updated_at": "2026-04-15",
        "number": "0009876-54.2024.8.21.0001",
        "court": "TJRS",
        "parts": "Tech Solutions Ltda vs. Fornecedor XYZ",
        "start_date": "2024-02-01",
        "status": "Aguardando sentença",
        "favorite": False,
        "client_id": 2,
        "tribunal_id": 2,
        "advogado_id": 1,
        "movements": [
            {"date": "2024-02-01", "description": "Distribuição da ação"},
        ],
    },
    {
        "id": 3,
        "created_at": "2026-04-14",
        "updated_at": "2026-04-16",
        "number": "0005555-11.2025.8.26.0100",
        "court": "STJ",
        "parts": "Maria Oliveira Silva vs. Operadora de Saúde",
        "start_date": "2025-01-10",
        "status": "Arquivado",
        "favorite": False,
        "client_id": 1,
        "tribunal_id": 3,
        "advogado_id": 2,
        "movements": [],
    },
]


def get_store() -> list[dict[str, Any]]:
    return _db


def get_by_id(process_id: int) -> dict[str, Any] | None:
    for item in _db:
        if item["id"] == process_id:
            return item
    return None


def toggle_favorite(process_id: int) -> dict[str, Any] | None:
    item = get_by_id(process_id)
    if item is None:
        return None
    item["favorite"] = not item["favorite"]
    return item
