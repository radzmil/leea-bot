"""Ujian sambungan laluan produksi tanpa rangkaian sebenar."""

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("GEMINI_API_KEY", "test-only")

import app


class ConnectionsTest(unittest.TestCase):
    def test_demo_and_engine(self):
        engine = app.CLIENT_ENGINES["architechlaboratory"]
        self.assertEqual(engine.one_off_setup_fee, 499.00)
        self.assertIn("PANDUAN SOKONGAN TEKNIKAL", engine.brain.persona_instruction)
        with patch.object(app.client.models, "generate_content") as generate:
            answer = app.generate_ai_response("contoh invois")
            self.assertIn("BUKAN INVOIS SAH", answer)
            generate.assert_not_called()

    def test_gemini_and_fallback(self):
        with patch.object(app.client.models, "generate_content") as generate:
            generate.return_value.text = "jawapan ujian"
            self.assertEqual(app.generate_ai_response("soalan biasa", "aluzlia"), "jawapan ujian")
            self.assertIn("Aluzlia", generate.call_args.kwargs["config"]["system_instruction"])
            self.assertIn("1–2 ayat pendek", generate.call_args.kwargs["config"]["system_instruction"])
            generate.side_effect = RuntimeError("Gemini unavailable")
            self.assertIn("RM130", app.generate_ai_response("harga pakej"))

    def test_image_payload_without_network(self):
        with patch.object(app.requests, "post") as post:
            post.return_value.ok = True
            self.assertTrue(app.send_whatsapp_image("id", "token", "6012", "https://example.org/item.png"))
            self.assertEqual(post.call_args.kwargs["json"]["type"], "image")
            self.assertFalse(app.send_whatsapp_image("id", "token", "6012", "http://example.org/item.png"))
            self.assertEqual(post.call_count, 1)


if __name__ == "__main__":
    unittest.main()