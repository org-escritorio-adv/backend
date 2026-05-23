import unittest
from datetime import date, datetime
from types import SimpleNamespace

from src.processos.repository import _to_process
from src.processos.schema import Process


class TestProcessosRepository(unittest.TestCase):
    def test_to_process_mapeia_campos(self):
        processo = SimpleNamespace(
            id=1,
            created_at=datetime(2026, 4, 10),
            updated_at=datetime(2026, 4, 10),
            numero_cnj="0001234-56.2023.8.26.0000",
            tribunal="TJSP",
            partes="João vs. Meta",
            data_abertura=datetime(2023, 5, 15),
            status="Em andamento",
            favorito=True,
            cliente_id=1,
            advogado_id=1,
            movimentacoes=[],
        )
        resultado = _to_process(processo)
        self.assertEqual(resultado.number, "0001234-56.2023.8.26.0000")
        self.assertTrue(resultado.favorite)

    def test_schema_valida_process(self):
        processo = Process(
            id=1,
            created_at=date(2026, 4, 10),
            updated_at=date(2026, 4, 10),
            number="0001234-56.2023.8.26.0000",
            court="TJSP",
            parts="Partes",
            start_date=date(2023, 5, 15),
            status="Em andamento",
            client_id=1,
            tribunal_id=1,
            advogado_id=1,
        )
        self.assertEqual(processo.id, 1)


if __name__ == "__main__":
    unittest.main()
