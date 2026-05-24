import unittest
from datetime import datetime
from src.processos.schema import Processo, ProcessoCreate


class TestProcessosSchema(unittest.TestCase):
    def test_schema_valida_campos_obrigatorios(self):
        payload = ProcessoCreate(
            numero_cnj="0001234-56.2023.8.26.0000",
            tribunal="TJSP",
            partes="João da Silva vs. Empresa Meta",
            data_abertura=datetime(2023, 5, 15),
            status="Em andamento",
            favorito=True,
            cliente_id=1,
            advogado_id=1
        )
        self.assertEqual(payload.numero_cnj, "0001234-56.2023.8.26.0000")
        self.assertEqual(payload.tribunal, "TJSP")

    def test_schema_from_orm(self):
        class MockProcessoORM:
            def __init__(self):
                self.id = 1
                self.numero_cnj = "0001234-56.2023.8.26.0000"
                self.tribunal = "TJSP"
                self.partes = "João vs. Maria"
                self.data_abertura = datetime(2023, 5, 15)
                self.status = "ativo"
                self.favorito = False
                self.cliente_id = 1
                self.advogado_id = 2
                self.created_at = datetime(2026, 4, 10)
                self.updated_at = datetime(2026, 4, 10)
                self.movimentacoes = []

        orm = MockProcessoORM()
        processo = Processo.model_validate(orm)
        self.assertEqual(processo.id, 1)
        self.assertEqual(processo.numero_cnj, "0001234-56.2023.8.26.0000")
        self.assertFalse(processo.favorito)


if __name__ == "__main__":
    unittest.main()
