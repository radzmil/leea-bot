"""Ujian draf dokumen jualan tanpa panggilan rangkaian."""

import unittest

from sales_documents import get_sales_document
from payment_guidance import get_payment_guidance
from leea_engine import LEEASystemEngine


class SalesDocumentsTest(unittest.TestCase):
    def test_quote_uses_catalogue(self):
        result = get_sales_document("sebut harga Basic Plan untuk Ali", "architechsystems")
        self.assertIn("RM279.00", result)
        self.assertIn("Pelanggan: Ali", result)
        self.assertIn("BUKAN DOKUMEN RASMI", result)
        self.assertIn("Admin: 011-2368-7357", result)
        self.assertIn("akaun bayaran online sedang dikemas kini", result)

    def test_invoice_not_paid(self):
        result = get_sales_document("invois Pro-Plan untuk Syarikat ABC", "architechsystems")
        self.assertIn("RM629.00", result)
        self.assertIn("Tiada pesanan atau pembayaran direkod", result)

    def test_missing_information_and_tenant_isolation(self):
        self.assertIn("sila nyatakan nama", get_sales_document("invois", "architechsystems"))
        self.assertIn("katalog harga akaun ini belum", get_sales_document("invois Basic Plan untuk Ali", "aluzlia"))
        self.assertIsNone(get_sales_document("selamat pagi", "architechsystems"))

    def test_payment_guidance_before_ai_and_isolated_by_tenant(self):
        engine = LEEASystemEngine("Architech Systems")
        engine.tenant_username = "architechsystems"
        def unexpected_responder(*args):
            self.fail("Gemini tidak patut dipanggil untuk arahan bayaran")
        response = engine.process_incoming_whatsapp_message("6012", "boleh bayar QR?", unexpected_responder)
        self.assertIn("011-2368-7357", response)
        self.assertIn("sedang dikemas kini", response)
        self.assertIsNone(get_payment_guidance("bayar QR", "aluzlia"))


if __name__ == "__main__":
    unittest.main()