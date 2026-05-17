import unittest

from src.leads.repository import get_store
from src.leads.schema import LeadSite


class TestLeadsRepository(unittest.TestCase):
    def test_schema_valida_mock(self):
        LeadSite.model_validate(get_store()[0])


if __name__ == "__main__":
    unittest.main()
