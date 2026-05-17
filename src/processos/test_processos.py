import unittest

from src.processos.repository import get_by_id, toggle_favorite
from src.processos.schema import Process


class TestProcessosRepository(unittest.TestCase):
    def test_get_by_id_existente(self):
        item = get_by_id(1)
        self.assertIsNotNone(item)
        self.assertEqual(item["number"], "0001234-56.2023.8.26.0000")

    def test_get_by_id_inexistente(self):
        self.assertIsNone(get_by_id(9999))

    def test_toggle_favorite(self):
        antes = get_by_id(2)["favorite"]
        toggle_favorite(2)
        depois = get_by_id(2)["favorite"]
        self.assertNotEqual(antes, depois)
        toggle_favorite(2)

    def test_schema_valida_mock(self):
        item = get_by_id(1)
        processo = Process.model_validate(item)
        self.assertEqual(processo.id, 1)


if __name__ == "__main__":
    unittest.main()
