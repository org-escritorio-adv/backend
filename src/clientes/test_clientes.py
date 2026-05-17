import unittest

from src.clientes.repository import get_store
from src.clientes.schema import Client


class TestClientesRepository(unittest.TestCase):
    def test_lista_mock(self):
        self.assertGreaterEqual(len(get_store()), 1)

    def test_schema_valida_mock(self):
        Client.model_validate(get_store()[0])


if __name__ == "__main__":
    unittest.main()
