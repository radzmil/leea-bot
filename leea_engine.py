"""
Nama Modul: leea_engine.py
Penerangan: Enjin Teras Sistem Automasi & Pemasaran Omnichannel (Architech Systems - SEA Bot)
Pemilik: Architech Systems (SSM: 202603255098 / 003893898-X)
Arkitek Sistem: Radzmil Amaluz Zamani Bin Raduen
"""

from leea_brain import LEEABrain

class LEEASystemEngine:
    def __init__(self, client_name: str, package_type: str = "Pro-Plan"):
        self.company_name = "Architech Systems"
        self.ssm_number = "202603255098 (003893898-X)"
        self.website = "www.architechsystems.my"
        self.address = "Laman Niaga, Jalan AWF5, Ampang Waterfront, 68000 Ampang, Selangor"
        self.system_name = "SEA Bot (WhatsApp)"
        self.client_name = client_name
        self.package_type = package_type
        
        self.brain = LEEABrain(client_name=self.client_name, business_sop="SOP Rasmi Architech Systems")
        
        self.packages = {
            "Basic Plan": {"setup_fee_one_off": 149.00, "monthly_fee": 130.00},
            "Pro-Plan": {"setup_fee_one_off": 499.00, "monthly_fee": 130.00},
            "Advance-Plan": {"setup_fee_one_off": 999.00, "monthly_fee": 130.00},
            "Custom Plan": {"setup_fee_one_off": "Rundingan Teknikal", "monthly_fee": 130.00}
        }
        
        current_pkg = self.packages.get(package_type, self.packages["Pro-Plan"])
        self.one_off_setup_fee = current_pkg["setup_fee_one_off"]
        self.monthly_subscription_fee = current_pkg["monthly_fee"]
        self.free_chat_tokens = 1000
        self.used_chat_tokens = 4
        self.is_active = True
        self.ai_mode = True

    def process_incoming_whatsapp_message(self, sender_phone: str, message_text: str) -> str:
        if not self.is_active:
            return "Sistem tidak aktif."
        if self.ai_mode:
            response = self.brain.generate_response(message_text)
            self.used_chat_tokens += 1
            return response
        else:
            return f"[HUMAN TOUCH] Mesej daripada {sender_phone} dialihkan kepada pegawai bertugas Architech Systems."