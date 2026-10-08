import unittest
from unittest.mock import patch

import database


class DatabaseTest(unittest.TestCase):
    def test_connect_uses_supplied_url_without_leaking_it(self):
        with patch.object(database.psycopg2, "connect") as connect:
            database.connect("postgresql://example.invalid/test")
        connect.assert_called_once_with("postgresql://example.invalid/test", connect_timeout=5)

    def test_connect_requires_configuration(self):
        with patch.object(database, "DATABASE_URL", None):
            with self.assertRaisesRegex(RuntimeError, "DATABASE_URL is not set"):
                database.connect()