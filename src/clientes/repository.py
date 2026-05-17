from typing import Any

_db: list[dict[str, Any]] = [
    {
        "id": 1,
        "created_at": "2026-03-01",
        "updated_at": "2026-03-15",
        "nome_razao_social": "Maria Oliveira Silva",
        "cpf_cnpj": "123.456.789-00",
        "telefone": "(11) 98765-4321",
        "email": "maria.oliveira@email.com",
    },
    {
        "id": 2,
        "created_at": "2026-03-10",
        "updated_at": "2026-04-02",
        "nome_razao_social": "Tech Solutions Ltda",
        "cpf_cnpj": "12.345.678/0001-90",
        "telefone": "(21) 3333-4444",
        "email": "contato@techsolutions.com.br",
    },
    {
        "id": 3,
        "created_at": "2026-04-05",
        "updated_at": "2026-04-05",
        "nome_razao_social": "João Pedro Santos",
        "cpf_cnpj": "987.654.321-00",
        "telefone": None,
        "email": "joao.santos@email.com",
    },
]


def get_store() -> list[dict[str, Any]]:
    return _db
