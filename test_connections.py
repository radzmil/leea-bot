"""Ujian sambungan laluan produksi tanpa rangkaian sebenar."""

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("ASAI_API_KEY", "test-only")

import app


class ConnectionsTest(unittest.TestCase):
    def test_wrong_phone_id_never_replies(self):
        tenant = app.CLIENTS_DATABASE["architechsystems"]
        with patch.dict(tenant, {"live_chats": [], "whatsapp_phone_id": "correct"}), \
             patch.object(app, "claim_incoming_message") as claim, \
             patch.object(app, "send_whatsapp_message") as send:
            payload = {"object": "whatsapp_business_account", "entry": [{"changes": [{"value": {
                "metadata": {"phone_number_id": "other"},
                "messages": [{"id": "mid", "from": "60111", "text": {"body": "Ticket ape ni?"}}]
            }}]}]}
            self.assertEqual(app.app.test_client().post("/webhook", json=payload).status_code, 200)
            claim.assert_not_called()
            send.assert_not_called()

    def test_database_claim_is_atomic_and_fails_closed(self):
        with patch.object(app, "DATABASE_URL", ""):
            self.assertIsNone(app.claim_incoming_message("architechsystems", "mid"))
        with patch.object(app, "DATABASE_URL", "postgres://test"), \
             patch.object(app.database, "connect") as connect:
            cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
            cursor.fetchone.side_effect = [("mid",), None]
            self.assertTrue(app.claim_incoming_message("architechsystems", "mid"))
            self.assertFalse(app.claim_incoming_message("architechsystems", "mid"))
            self.assertIn("ON CONFLICT DO NOTHING", cursor.execute.call_args.args[0])
            connect.side_effect = RuntimeError("db down")
            self.assertIsNone(app.claim_incoming_message("architechsystems", "new"))

    def test_webhook_retries_when_database_claim_fails(self):
        tenant = app.CLIENTS_DATABASE["architechsystems"]
        payload = {"object": "whatsapp_business_account", "entry": [{"changes": [{"value": {
            "metadata": {"phone_number_id": "bot-phone-id"},
            "messages": [{"id": "mid", "from": "60111", "text": {"body": "Hai"}}]
        }}]}]}
        with patch.dict(tenant, {"live_chats": [], "whatsapp_phone_id": "bot-phone-id"}), \
             patch.object(app, "claim_incoming_message", return_value=None), \
             patch.object(app, "send_whatsapp_message") as send:
            response = app.app.test_client().post("/webhook", json=payload)
            self.assertEqual(response.status_code, 503)
            send.assert_not_called()
            self.assertEqual(tenant["live_chats"], [])

    def test_webhook_retries_when_incoming_message_cannot_be_saved(self):
        tenant = app.CLIENTS_DATABASE["architechsystems"]
        payload = {"object": "whatsapp_business_account", "entry": [{"changes": [{"value": {
            "metadata": {"phone_number_id": "bot-phone-id"},
            "messages": [{"id": "mid", "from": "60111", "text": {"body": "Hai"}}]
        }}]}]}
        with patch.dict(tenant, {"live_chats": [], "whatsapp_phone_id": "bot-phone-id"}), \
             patch.object(app, "claim_incoming_message", return_value=True), \
             patch.object(app, "release_incoming_message") as release, \
             patch.object(app, "load_chat_context", return_value=[]), \
             patch.object(app, "save_customer_to_google_sheets"), \
             patch.object(app, "save_chat_history_to_sheets"), \
             patch.object(app, "save_chat_to_postgres", return_value=False), \
             patch.object(app, "send_whatsapp_message") as send:
            response = app.app.test_client().post("/webhook", json=payload)
            self.assertEqual(response.status_code, 503)
            release.assert_called_once_with("architechsystems", "mid")
            send.assert_not_called()
            self.assertEqual(tenant["live_chats"], [])

    def test_save_chat_reports_missing_database_and_missing_tenant(self):
        with patch.object(app, "DATABASE_URL", ""):
            self.assertFalse(app.save_chat_to_postgres("architechsystems", "60111", "Hai"))
        with patch.object(app, "DATABASE_URL", "postgres://test"), \
             patch.object(app.database, "connect") as connect:
            connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value.fetchone.return_value = None
            self.assertFalse(app.save_chat_to_postgres("architechsystems", "60111", "Hai"))

    def test_webhook_ignores_outbound_echo(self):
        tenant = app.CLIENTS_DATABASE["architechsystems"]
        with patch.dict(tenant, {"live_chats": [], "whatsapp_phone_id": "bot-phone-id"}), \
             patch.object(app, "PROCESSED_MESSAGE_IDS", {}), \
             patch.object(app, "generate_ai_response") as generate, \
             patch.object(app, "send_whatsapp_message") as send:
            for index, fields in enumerate(({"from_me": True, "from_user_id": "MY.customer"},
                                             {"direction": "outbound", "from_user_id": "MY.customer"},
                                             {"from": "60123456789"},
                                             {"from": "bot-phone-id"})):
                payload = {"object": "whatsapp_business_account", "entry": [{"changes": [{"value": {
                    "metadata": {"display_phone_number": "+60123456789", "phone_number_id": "bot-phone-id"},
                    "messages": [{"id": f"echo-{index}", "text": {"body": "Balasan bot"}, **fields}]
                }}]}]}
                self.assertEqual(app.app.test_client().post("/webhook", json=payload).status_code, 200)
            generate.assert_not_called()
            send.assert_not_called()
            self.assertEqual(tenant["live_chats"], [])

    def test_whatsapp_reply_has_no_role_prefix(self):
        for label in ("💬 [Pegawai Khidmat Pelanggan - Architech Systems]",
                      "💬 [Pegawai Khidmat Pelanggan - Architech Systems (CLI-1001)]",
                      "[Customer Service - Architech Systems]"):
            self.assertEqual(app.clean_whatsapp_reply(f"{label}: Baik, boleh saya bantu?"),
                             "Baik, boleh saya bantu?")
        with patch.object(app.requests, "post") as post:
            app.send_whatsapp_message("id", "token", "6012", "💬 [Pegawai Khidmat Pelanggan - Architech Systems]: Waalaikumussalam!")
            self.assertEqual(post.call_args.kwargs["json"]["text"]["body"], "Waalaikumussalam!")

    def test_demo_and_engine(self):
        engine = app.CLIENT_ENGINES["architechsystems"]
        self.assertEqual(engine.brain.client_id, "CLI-1001")
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
            self.assertNotIn("Gerak Gempur Cikgu Leea", instruction)
            self.assertIn("1–2 ayat pendek", instruction)
            self.assertIn("Jangan berpura-pura menjadi manusia", instruction)
            self.assertIn("jangan guna senarai bernombor, bullet atau menu pilihan", instruction)
            self.assertIn("Bahasa Melayu Malaysia", instruction)
            self.assertIn("jangan beralih ke Bahasa Indonesia", instruction)
            self.assertIn("bahasa pasar atau singkatan", instruction)
            self.assertEqual(generate.call_args.kwargs["json"]["model"], "asai/claude-haiku-4.5")
            generate.side_effect = RuntimeError("asAI unavailable")
            self.assertIn("RM130", app.generate_ai_response("harga pakej"))

    def test_architech_website_knowledge_is_in_prompt(self):
        from company_knowledge import load_company_knowledge
        knowledge = load_company_knowledge("architechsystems")
        self.assertIn("SENARIO ILUSTRASI", knowledge)
        self.assertIn("demo atau simulasi sistem", knowledge)
        self.assertIn("versi 1 sudah penuh", knowledge)
        self.assertIn("kapasiti pengguna akan ditambah", knowledge)
        self.assertIn("pasukan sales akan menghubungi", knowledge)
        self.assertNotIn("Gerak Gempur Cikgu Leea", load_company_knowledge("aluzlia"))
        self.assertEqual(load_company_knowledge("unknown"), "")
        with patch.object(app.requests, "post") as generate:
            generate.return_value.json.return_value = {"choices": [{"message": {"content": "Baik"}}]}
            app.generate_ai_response("Apa contoh penyelesaian di laman?")
            instruction = generate.call_args.kwargs["json"]["messages"][0]["content"]
            self.assertIn("latihan kuiz interaktif", instruction)
            self.assertIn("versi 1 sudah penuh", instruction)
            self.assertIn("bukan kajian kes sebenar", instruction)

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

    def test_repeated_answer_is_regenerated_without_repeating_question(self):
        history = [{"sender": "agent", "text": "Pakej mana tuan mahu?"}]
        with patch.object(app.requests, "post") as post:
            post.return_value.json.side_effect = [
                {"choices": [{"message": {"content": "Pakej mana tuan mahu?"}}]},
                {"choices": [{"message": {"content": "Tiket merujuk kepada permintaan sokongan."}}]},
            ]
            result = app.generate_ai_response("Ticket ape ni?", "aluzlia", "6012", history)
            self.assertEqual(result, "Tiket merujuk kepada permintaan sokongan.")
            self.assertEqual(post.call_count, 2)
            self.assertIn("soalan sebenar", post.call_args.kwargs["json"]["messages"][0]["content"])

    def test_persistent_repeated_answer_uses_distinct_clarification(self):
        history = [{"sender": "agent", "text": "Pakej mana tuan mahu?"}]
        with patch.object(app.requests, "post") as post:
            post.return_value.json.return_value = {
                "choices": [{"message": {"content": "Pakej mana tuan mahu?"}}]}
            result = app.generate_ai_response("Ticket ape ni?", "aluzlia", "6012", history)
            self.assertNotEqual(result, history[0]["text"])
            self.assertEqual(post.call_count, 2)

    def test_fixed_reply_and_fallback_do_not_repeat_question(self):
        history = [{"sender": "agent", "text": "Sila pilih tepat satu pelan: Basic Plan, Pro-Plan atau Advance-Plan. Pelan Custom perlu harga disahkan staf."},
                   {"sender": "customer", "text": "Saya belum pasti."}]
        with patch.object(app.requests, "post") as post:
            result = app.generate_ai_response("invois Basic Plan dan Pro-Plan untuk Ali",
                                              "architechsystems", "6012", history)
            self.assertNotIn("Sila pilih tepat satu pelan", result)
            self.assertIn("staf", result)
            post.assert_not_called()

        history = [{"sender": "agent", "text": "Pakej mana tuan mahu?"},
                   {"sender": "customer", "text": "Saya jual kek. Harga pakej?"}]
        with patch.object(app.requests, "post") as post, \
             patch.object(app.CLIENT_ENGINES["aluzlia"].brain, "generate_response",
                          return_value="Harga RM130. Pakej mana tuan mahu?"):
            post.side_effect = RuntimeError("offline")
            result = app.generate_ai_response("Harga pakej?", "aluzlia", "6012", history)
            self.assertNotIn("Pakej mana tuan mahu?", result)
            self.assertIn("staf", result)

    def test_paraphrased_punctuation_and_history_scope(self):
        history = [{"sender": "agent", "text": "Pakej mana tuan mahu?"},
                   {"sender": "customer", "text": "Pakej mana tuan mahu?"}]
        self.assertTrue(app.repeated_reply("Pakej mana tuan mahu ?", history))
        self.assertFalse(app.repeated_reply("Pakej mana tuan mahu?", history[1:]))
        self.assertFalse(app.repeated_reply("Harga Basic ialah RM149.", history))

    def test_approved_knowledge_is_tenant_specific(self):
        with patch.object(app.requests, "post") as generate:
            generate.return_value.json.return_value = {"choices": [{"message": {"content": "Baik."}}]}
            app.generate_ai_response("Apa beza produk?", "architechsystems")
            self.assertIn("projek mengikut keperluan", generate.call_args.kwargs["json"]["messages"][0]["content"])
            app.generate_ai_response("Apa beza produk?", "aluzlia")
            self.assertNotIn("projek mengikut keperluan", generate.call_args.kwargs["json"]["messages"][0]["content"])

    def test_missing_asai_key_does_not_send_customer_chat(self):
        with patch.object(app, "ASAI_API_KEY", ""), patch.object(app.requests, "post") as post:
            self.assertTrue(app.generate_ai_response("harga pakej"))
            post.assert_not_called()

    def test_context_database_is_scoped(self):
        with patch.object(app, "DATABASE_URL", "test-db"), patch.object(app.database, "connect") as connect:
            cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
            cursor.fetchone.return_value = (42,)
            cursor.fetchall.return_value = [("Zulfa Bot", "Baik"), ("6012", "Saya jual kek")]
            result = app.load_chat_context("aluzlia", "6012")
            self.assertEqual(result[-1]["text"], "Baik")
            self.assertEqual(cursor.execute.call_args_list[0].args[1], ("aluzlia",))
            self.assertEqual(cursor.execute.call_args_list[1].args[1], (42, "6012", 10))
            self.assertIn("prospect_phone = %s", cursor.execute.call_args_list[1].args[0])

    def test_webhook_duplicate_and_distinct_prospects(self):
        tenant = app.CLIENTS_DATABASE["architechsystems"]
        seen = set()
        def claim(_tenant, message_id):
            if message_id in seen:
                return False
            seen.add(message_id)
            return True
        with patch.dict(tenant, {"live_chats": [], "whatsapp_phone_id": "bot-phone-id"}), patch.object(app, "PROCESSED_MESSAGE_IDS", {}), patch.object(app, "DATABASE_URL", ""), \
             patch.object(app, "claim_incoming_message", side_effect=claim), \
             patch.object(app, "load_chat_context", return_value=[]), \
             patch.object(app, "save_customer_to_google_sheets"), \
             patch.object(app, "save_chat_history_to_sheets"), \
             patch.object(app, "save_chat_to_postgres"), \
             patch.object(app, "generate_ai_response", return_value="Baik") as generate, \
             patch.object(app, "send_whatsapp_message") as send:
            for phone, msg_id in (("60111", "mid-1"), ("60222", "mid-2"), ("60111", "mid-1")):
                payload = {"object": "whatsapp_business_account", "entry": [{"changes": [{"value": {
                    "metadata": {"phone_number_id": "bot-phone-id"},
                    "messages": [{"id": msg_id, "from": phone, "text": {"body": "Hai"}}]
                }}]}]}
                self.assertEqual(app.app.test_client().post("/webhook", json=payload).status_code, 200)
            self.assertEqual(send.call_count, 2)
            self.assertEqual([call.args[2] for call in send.call_args_list], ["60111", "60222"])
            self.assertEqual(len(tenant["live_chats"]), 2)
            self.assertEqual(generate.call_count, 2)

    def test_webhook_from_user_id_is_not_treated_as_phone_number(self):
        tenant = app.CLIENTS_DATABASE["architechsystems"]
        sender_id = "MY.1689129625508391"
        with patch.dict(tenant, {"live_chats": [], "whatsapp_phone_id": "bot-phone-id"}), patch.object(app, "PROCESSED_MESSAGE_IDS", {}), patch.object(app, "DATABASE_URL", ""), \
             patch.object(app, "claim_incoming_message", side_effect=[True, False]), \
             patch.object(app, "load_chat_context", return_value=[]) as load_context, \
             patch.object(app, "save_customer_to_google_sheets"), \
             patch.object(app, "save_chat_history_to_sheets"), \
             patch.object(app, "save_chat_to_postgres"), \
             patch.object(app, "generate_ai_response", return_value="Hai!") as generate, \
             patch.object(app, "send_whatsapp_message") as send:
            payload = {"object": "whatsapp_business_account", "entry": [{"changes": [{"value": {
                "metadata": {"phone_number_id": "bot-phone-id"},
                "messages": [{"id": "wamid-test", "from_user_id": sender_id,
                              "text": {"body": "Haluuuuu"}, "type": "text"}]
            }}]}]}
            self.assertEqual(app.app.test_client().post("/webhook", json=payload).status_code, 200)
            self.assertEqual(tenant["live_chats"][0]["phone"], sender_id)
            load_context.assert_called_once_with("architechsystems", sender_id)
            self.assertEqual(generate.call_args.args[2], sender_id)
            self.assertEqual(send.call_args.args[2], sender_id)
            self.assertEqual(app.app.test_client().post("/webhook", json=payload).status_code, 200)
            self.assertEqual(send.call_count, 1)

    def test_meta_rejection_does_not_record_bot_reply(self):
        tenant = app.CLIENTS_DATABASE["architechsystems"]
        with patch.dict(tenant, {"live_chats": [], "whatsapp_phone_id": "phone-id", "whatsapp_token": "token"}), \
             patch.object(app, "PROCESSED_MESSAGE_IDS", {}), patch.object(app, "DATABASE_URL", ""), \
             patch.object(app, "claim_incoming_message", return_value=True), \
             patch.object(app, "load_chat_context", return_value=[]), \
             patch.object(app, "save_customer_to_google_sheets"), \
             patch.object(app, "save_chat_history_to_sheets"), \
             patch.object(app, "save_chat_to_postgres") as save, \
             patch.object(app, "generate_ai_response", return_value="Hai!"), \
             patch.object(app.requests, "post") as post:
            post.return_value.ok = False
            post.return_value.status_code = 400
            post.return_value.text = '{"error":"Invalid recipient"}'
            payload = {"object": "whatsapp_business_account", "entry": [{"changes": [{"value": {
                "metadata": {"phone_number_id": "phone-id"},
                "messages": [{"id": "wamid-rejected", "from_user_id": "MY.1689129625508391",
                              "text": {"body": "Haluuuuu"}, "type": "text"}]
            }}]}]}
            self.assertEqual(app.app.test_client().post("/webhook", json=payload).status_code, 200)
            self.assertEqual(post.call_args.kwargs["json"]["to"], "MY.1689129625508391")
            self.assertEqual(save.call_count, 1)
            self.assertEqual(len(tenant["live_chats"][0]["messages"]), 1)

    def test_image_payload_without_network(self):
        with patch.object(app.requests, "post") as post:
            post.return_value.ok = True
            self.assertTrue(app.send_whatsapp_image("id", "token", "6012", "https://example.org/item.png"))
            self.assertEqual(post.call_args.kwargs["json"]["type"], "image")
            self.assertFalse(app.send_whatsapp_image("id", "token", "6012", "http://example.org/item.png"))
            self.assertEqual(post.call_count, 1)


if __name__ == "__main__":
    unittest.main()