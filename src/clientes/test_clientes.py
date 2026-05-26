import unittest
from datetime import datetime
from types import SimpleNamespace
import pytest
from pydantic import ValidationError

from src.clientes.schema import Client, ClientCreate, ClientUpdate


class TestClientesSchema(unittest.TestCase):
    def test_client_create_herda_campos_obrigatorios(self):
        payload = ClientCreate(
            nome_razao_social="Maria Silva",
            cpf_cnpj="123.456.789-00",
        )
        self.assertEqual(payload.nome_razao_social, "Maria Silva")

    def test_client_update_parcial(self):
        payload = ClientUpdate(telefone="(11) 99999-0000")
        dumped = payload.model_dump(exclude_unset=True)
        self.assertEqual(dumped, {"telefone": "(11) 99999-0000"})

    def test_client_from_orm(self):
        orm = SimpleNamespace(
            id=1,
            nome_razao_social="Maria Silva",
            cpf_cnpj="123.456.789-00",
            telefone=None,
            email="maria@email.com",
            created_at=datetime(2026, 3, 1, 12, 0, 0),
            updated_at=None,
        )
        client = Client.model_validate(orm)
        self.assertEqual(client.id, 1)
        self.assertIsNone(client.updated_at)


@pytest.mark.parametrize(
    "nome, cpf_cnpj, telefone, email, expect_valid",
    [
        ("Maria Silva", "123.456.789-00", "(11) 99999-0000", "maria@email.com", True),
        ("João da Silva", "12345678901", None, None, True),
        (None, "123.456.789-00", None, None, False),  # Nome é obrigatório (deve falhar)
        ("Maria Silva", None, None, None, False),  # CPF/CNPJ é obrigatório (deve falhar)
    ]
)
def test_client_create_validation_parametrizado(nome, cpf_cnpj, telefone, email, expect_valid):
    if expect_valid:
        client = ClientCreate(nome_razao_social=nome, cpf_cnpj=cpf_cnpj, telefone=telefone, email=email)
        assert client.nome_razao_social == nome
        assert client.cpf_cnpj == cpf_cnpj
    else:
        with pytest.raises(ValidationError):
            ClientCreate(nome_razao_social=nome, cpf_cnpj=cpf_cnpj, telefone=telefone, email=email)


if __name__ == "__main__":
    unittest.main()
