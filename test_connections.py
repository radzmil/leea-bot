"""Ujian sambungan laluan produksi tanpa rangkaian sebenar."""

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("ASAI_API_KEY", "test-only")

import app


class ConnectionsTest(unittest.TestCase):
    def test_demo_and_engine(self):
        engine = app.CLIENT_ENGINES["architechlaboratory"]
        self.assertEqual(engine.one_off_setup_fee, 499.00)
        self.assertIn("PANDUAN SOKONGAN TEKNIKAL", engine.brain.persona_instruction)
        with patch.object(app.requests, "post") as generate:
            answer = app.generate_ai_response("contoh invois")
            self.assertIn("BUKAN INVOIS SAH", answer)
            generate.assert_not_called()

    def test_asai_and_fallback(self):
        with patch.object(app.requests, "post") as generate:
            generate.return_value.json.return_value = {"choices": [{"message": {"content": "jawapan ujian"}}]}
            self.assertEqual(app.generate_ai_response("soalan biasa", "aluzlia"), "jawapan ujian")
            instruction = generate.call_args.kwargs["json"]["messages"][0]["content"]
            self.assertIn("Aluzlia", instruction)
            self.assertIn("1–2 ayat pendek", instruction)
            self.assertIn("Jangan berpura-pura menjadi manusia", instruction)
            self.assertEqual(generate.call_args.kwargs["json"]["model"], "asai/claude-haiku-4.5")
            generate.side_effect = RuntimeError("asAI unavailable")
            self.assertIn("RM130", app.generate_ai_response("harga pakej"))

    def test_short_reply_for_other_services(self):
        with patch.object(app.requests, "post") as generate:
            answer = app.generate_ai_response("Selain sistem Leea.. ade sistem ape lagi?")
            self.assertIn("automasi", answer)
            self.assertLessEqual(len(answer.split()), 25)
            self.assertNotIn("Salam", answer)
            generate.assert_not_called()
            app.generate_ai_response("Selain sistem Leea.. ade sistem ape lagi?", "aluzlia")
            generate.assert_called_once()

    def test_history_passed_to_asai_without_cross_tenant_memory(self):
        history = [{"sender": "customer", "text": "Saya jual kek"},
                   {"sender": "agent", "text": "Baik, saya faham."}]
        with patch.object(app.requests, "post") as generate:
            generate.return_value.json.return_value = {"choices": [{"message": {"content": "Boleh bantu tempahan kek."}}]}
            self.assertEqual(app.generate_ai_response("Macam mana?", "aluzlia", "6012", history),
                             "Boleh bantu tempahan kek.")
            contents = generate.call_args.kwargs["json"]["messages"]
            self.assertEqual([turn["role"] for turn in contents], ["system", "user", "assistant", "user"])
            self.assertEqual(contents[1]["content"], "Saya jual kek")
            self.assertEqual(contents[-1]["content"], "Macam mana?")
            self.assertIn("Jangan tanya perkara sama kali kedua",
                          contents[0]["content"])

    def test_approved_knowledge_is_tenant_specific(self):
        with patch.object(app.requests, "post") as generate:
            generate.return_value.json.return_value = {"choices": [{"message": {"content": "Baik."}}]}
            app.generate_ai_response("Apa beza produk?", "architechlaboratory")
            self.assertIn("projek mengikut keperluan", generate.call_args.kwargs["json"]["messages"][0]["content"])
            app.generate_ai_response("Apa beza produk?", "aluzlia")
            self.assertNotIn("projek mengikut keperluan", generate.call_args.kwargs["json"]["messages"][0]["content"])

    def test_missing_asai_key_does_not_send_customer_chat(self):
        with patch.object(app, "ASAI_API_KEY", ""), patch.object(app.requests, "post") as post:
            self.assertTrue(app.generate_ai_response("harga pakej"))
            post.assert_not_called()

    def test_context_database_is_scoped(self):
        with patch.object(app, "DATABASE_URL", "test-db"), patch.object(app.psycopg2, "connect") as connect:
            cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
            cursor.fetchone.return_value = (42,)
            cursor.fetchall.return_value = [("Zulfa Bot", "Baik"), ("6012", "Saya jual kek")]
            result = app.load_chat_context("aluzlia", "6012")
            self.assertEqual(result[-1]["text"], "Baik")
            self.assertEqual(cursor.execute.call_args_list[0].args[1], ("aluzlia",))
            self.assertEqual(cursor.execute.call_args_list[1].args[1][:2], (42, "6012"))

    def test_image_payload_without_network(self):
        with patch.object(app.requests, "post") as post:
            post.return_value.ok = True
            self.assertTrue(app.send_whatsapp_image("id", "token", "6012", "https://example.org/item.png"))
            self.assertEqual(post.call_args.kwargs["json"]["type"], "image")
            self.assertFalse(app.send_whatsapp_image("id", "token", "6012", "http://example.org/item.png"))
            self.assertEqual(post.call_count, 1)


if __name__ == "__main__":
    unittest.main()