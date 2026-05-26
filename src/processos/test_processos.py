import unittest
from datetime import datetime
import pytest
from pydantic import ValidationError

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


@pytest.mark.parametrize(
    "numero_cnj, tribunal, partes, favorito, expect_valid",
    [
        ("0001234-56.2023.8.26.0000", "TJSP", "João vs. Maria", True, True),
        ("9999999-99.2023.8.26.9999", "TRF1", None, False, True),
        (None, "TJSP", "João vs. Maria", True, False),  # numero_cnj é obrigatório
        ("0001234-56.2023.8.26.0000", None, "João vs. Maria", True, False),  # tribunal é obrigatório
    ]
)
def test_processo_create_validation_parametrizado(numero_cnj, tribunal, partes, favorito, expect_valid):
    if expect_valid:
        processo = ProcessoCreate(numero_cnj=numero_cnj, tribunal=tribunal, partes=partes, favorito=favorito)
        assert processo.numero_cnj == numero_cnj
        assert processo.tribunal == tribunal
    else:
        with pytest.raises(ValidationError):
            ProcessoCreate(numero_cnj=numero_cnj, tribunal=tribunal, partes=partes, favorito=favorito)


if __name__ == "__main__":
    unittest.main()
