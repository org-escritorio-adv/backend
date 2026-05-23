import unittest
from datetime import datetime
from types import SimpleNamespace

from src.leads.schema import LeadSite


class TestLeadsSchema(unittest.TestCase):
    def test_lead_from_orm(self):
        orm = SimpleNamespace(
            id=1,
            criado_em=datetime(2026, 4, 1),
            atualizado_em=datetime(2026, 4, 5),
            nome="Ana Costa",
            email="ana.costa@email.com",
            telefone="(11) 91234-5678",
            mensagem="Consulta trabalhista.",
            status="Novo",
        )
        lead = LeadSite.model_validate(orm)
        self.assertEqual(lead.id, 1)
        self.assertEqual(lead.nome, "Ana Costa")


if __name__ == "__main__":
    unittest.main()
