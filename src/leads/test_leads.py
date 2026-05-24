import unittest
from src.leads.schema import LeadSite


class TestLeadsSchema(unittest.TestCase):
    def test_schema_valida_mock(self):
        mock_data = {
            "id": 1,
            "nome": "João da Silva",
            "email": "joao@email.com",
            "telefone": "11999999999",
            "mensagem": "Quero marcar uma consulta",
            "status": "Novo"
        }
        lead = LeadSite.model_validate(mock_data)
        self.assertEqual(lead.nome, "João da Silva")
        self.assertEqual(lead.status, "Novo")


if __name__ == "__main__":
    unittest.main()
