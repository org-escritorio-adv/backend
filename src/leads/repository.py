from typing import Any

_db: list[dict[str, Any]] = [
    {
        "id": 1,
        "criado_em": "2026-04-01",
        "atualizado_em": "2026-04-05",
        "nome": "Ana Costa",
        "email": "ana.costa@email.com",
        "telefone": "(11) 91234-5678",
        "mensagem": "Gostaria de uma consulta sobre direito trabalhista.",
        "status": "Novo",
    },
    {
        "id": 2,
        "criado_em": "2026-04-08",
        "atualizado_em": "2026-04-10",
        "nome": "Carlos Mendes",
        "email": "carlos.mendes@empresa.com",
        "telefone": "(31) 99876-5432",
        "mensagem": "Preciso de assessoria para abertura de empresa.",
        "status": "Em contato",
    },
    {
        "id": 3,
        "criado_em": "2026-04-12",
        "atualizado_em": "2026-04-12",
        "nome": "Fernanda Lima",
        "email": "fernanda.lima@email.com",
        "telefone": "(47) 98888-7777",
        "mensagem": "Tenho interesse em ação de indenização por danos morais.",
        "status": "Convertido",
    },
]


def get_store() -> list[dict[str, Any]]:
    return _db
