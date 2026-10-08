"""Ujian notifikasi WebSocket tanpa pangkalan data sebenar."""
import json
import os
import unittest
from unittest.mock import MagicMock, patch

from itsdangerous import URLSafeTimedSerializer

os.environ.setdefault("ASAI_API_KEY", "test-only")
import app
from chat_ticket import SALT


class ChatSocketTest(unittest.TestCase):
    def setUp(self):
        self.secret = "x" * 40
        self.origin = "https://portal.example"
        self.settings = patch.dict(os.environ, {
            "CHAT_SOCKET_SECRET": self.secret,
            "CHAT_SOCKET_ORIGIN": self.origin,
        })
        self.settings.start()
        self.addCleanup(self.settings.stop)

    def call_socket(self, ws, ticket, client_id=None):
        args = {"ticket": ticket}
        if client_id is not None:
            args["client_id"] = client_id
        with app.app.test_request_context("/ws/chat", query_string=args,
                                          headers={"Origin": self.origin}):
            app.chat_socket(ws)

    def test_rejects_invalid_or_other_tenant_ticket(self):
        with patch.object(app.database, "connect") as connect:
            for ticket in ("invalid", URLSafeTimedSerializer(self.secret, salt=SALT).dumps("aluzlia")):
                ws = MagicMock()
                self.call_socket(ws, ticket, "architechsystems")
                ws.close.assert_called_once()
            connect.assert_not_called()

    def test_notifies_only_authorized_tenant(self):
        ticket = URLSafeTimedSerializer(self.secret, salt=SALT).dumps("architechsystems")
        ws = MagicMock()
        connection = MagicMock()
        connection.notifies = [MagicMock(payload="aluzlia"), MagicMock(payload="architechsystems")]
        with patch.object(app, "DATABASE_URL", "postgres://test"), \
             patch.object(app.database, "connect", return_value=connection) as connect, \
             patch.object(app.select, "select", side_effect=[([connection], [], []), OSError("closed")]):
            self.call_socket(ws, ticket, "aluzlia")
        connect.assert_called_once_with("postgres://test")
        self.assertEqual(json.loads(ws.send.call_args.args[0]),
                         {"type": "chat_changed", "client_id": "architechsystems"})
        self.assertEqual(ws.send.call_count, 1)
        connection.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()