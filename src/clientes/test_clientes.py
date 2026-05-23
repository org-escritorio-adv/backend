import unittest
from datetime import datetime
from types import SimpleNamespace

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


if __name__ == "__main__":
    unittest.main()
