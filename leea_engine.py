"""
Nama Modul: leea_engine.py
Penerangan: Enjin Teras Sistem Automasi & Pemasaran Omnichannel (LEEA System)
Pemilik: Architech Laboratory (Di bawah entiti Epiphytes Services)
Arkitek Sistem: Radzmil Amaluz Zamani Bin Raduen
Pengarah / Pengasas: Hasliana Binti Annuar Hashim
"""

# Menghubungkan modul leea_brain.py secara rasmi ke dalam enjin sistem
from leea_brain import LEEABrain

class LEEASystemEngine:
    def __init__(self, client_name: str, package_type: str = "Pro"):
        self.company_name = "Architech Laboratory"
        self.parent_company = "Epiphytes Services"
        self.system_name = "LEEA System"
        self.client_name = client_name
        self.package_type = package_type
        
        # Integrasi penuh LEEABrain (mengambil persona, SOP, & peraturan sulit nombor/founder)
        self.brain = LEEABrain(client_name=self.client_name, business_sop="SOP Rasmi Perniagaan")
        
        # Struktur Harga Pakej Rasmi LEEA System
        self.packages = {
            "Basic": {
                "setup_fee_one_off": 150.00,
                "monthly_fee": 130.00,
                "target": "Sesuai untuk perniagaan kecil, solopreneur, atau peniaga online.",
                "features": "Profil asas, FAQ 20-30 soalan, skrip standard, web dashboard asas, pautan manual admin (Tiada Human Touch)."
            },
            "Pro": {
                "setup_fee_one_off": 450.00,
                "monthly_fee": 130.00,
                "target": "Sesuai untuk PKS (SME) dengan pasukan Customer Service (Paling Popular).",
                "features": "Persona tersuai, katalog produk terperinci, sales flow, dashboard Pro, fungsi hibrid Human Touch, QR Code & butang resit 'Done'."
            },
            "Advance": {
                "setup_fee_one_off": 1000.00,
                "monthly_fee": 130.00,
                "target": "Automation untuk syarikat besar dengan spesifikasi penuh.",
                "features": "Conditional logic, sambung database/stok, dashboard korporat, sokongan hibrid tanpa had, ToyyibPay/Webhook callback realtime."
            },
            "Custom": {
                "setup_fee_one_off": "Direct Teknikal (Custom Price)",
                "monthly_fee": 130.00,
                "target": "Keperluan khas luar kotak, perlu direct teknikal untuk tetapkan harga setup.",
                "features": "Skop kerja khusus mengikut keperluan operasi syarikat."
            }
        }
        
        # Tetapkan pakej semasa klien
        current_pkg = self.packages.get(package_type, self.packages["Pro"])
        self.one_off_setup_fee = current_pkg["setup_fee_one_off"]
        self.monthly_subscription_fee = current_pkg["monthly_fee"]
        
        # Kuota Token & Status
        self.free_chat_tokens = 1000
        self.used_chat_tokens = 4
        self.is_active = True
        self.ai_mode = True  # True = AI Auto-Pilot (LEEABrain), False = Human Touch

    def get_system_profile(self) -> dict:
        """Memaparkan profil korporat dan maklumat terperinci pakej sistem."""
        return {
            "system": self.system_name,
            "laboratory": self.company_name,
            "parent_entity": self.parent_company,
            "architect": "Radzmil Amaluz Zamani Bin Raduen",
            "client": self.client_name,
            "selected_package": self.package_type,
            "package_details": self.packages.get(self.package_type, {}),
            "monthly_subscription_myr": self.monthly_subscription_fee
        }

    def get_client_dashboard(self) -> dict:
        """
        Modul Dashboard Pelanggan & Fungsi Utama:
        Membantu klien memantau operasi bot, status langganan, dan analitis chat secara real-time.
        """
        remaining_tokens = self.free_chat_tokens - self.used_chat_tokens
        
        dashboard_data = {
            "client_name": self.client_name,
            "system_status": "Aktif & Beroperasi (24/7)" if self.is_active else "Tidak Aktif",
            "current_mode": "AI Auto-Pilot (LEEABrain Aktif Melayan SOP)" if self.ai_mode else "Human Touch (Mod Manual)",
            "subscription_status": f"Aktif ({self.package_type} Plan - RM{self.monthly_subscription_fee}/bulan)",
            "token_usage": {
                "total_allocated": self.free_chat_tokens,
                "used": self.used_chat_tokens,
                "remaining": remaining_tokens
            },
            "dashboard_features_guide": {
                "1. Live Chat & Bot Control": "Pusat untuk melihat mesej WhatsApp masuk secara langsung dan menukar mod kepada Human Touch jika mahu balas sendiri.",
                "2. Token & Billing Monitor": "Memantau baki kuota chat percuma bulanan serta status pembayaran langganan melalui ToyyibPay.",
                "3. Analytics & Performance": "Meneliti jumlah pelanggan yang dilayan bot dan prestasi jawapan mengikut SOP bisnes.",
                "4. Profile Settings": "Tempat mengemaskini maklumat syarikat, nombor telefon, dan tetapan asas akaun."
            }
        }
        return dashboard_data

    def get_subscription_and_setup_guide(self) -> str:
        """Penerangan lengkap mengenai pelan pakej LEEA System dan caj one-off setup."""
        guide = (
            f"=== PANDUAN PELAN PAKEJ & SETUP {self.system_name} ===\n\n"
            f"1. Pakej Basic (Setup RM150 One-Time | Bulanan RM130):\n"
            f"   - Sesuai untuk biz kecil/solopreneur. Profil asas, FAQ 20-30 soalan, skrip standard, dashboard asas.\n\n"
            f"2. Pakej Pro [Paling Popular] (Setup RM450 One-Time | Bulanan RM130):\n"
            f"   - Sesuai untuk PKS/SME. Persona tersuai, katalog produk, sales flow, dashboard Pro, Hibrid Human Touch, QR Code & butang resit 'Done'.\n\n"
            f"3. Pakej Advance (Setup RM1,000 One-Time | Bulanan RM130):\n"
            f"   - Sesuai untuk syarikat besar. Conditional logic, sambung database/stok, dashboard korporat, ToyyibPay/Webhook realtime & dokumen lengkap.\n\n"
            f"4. Pakej Custom (Direct Teknikal - Custom Price):\n"
            f"   - Keperluan khas luar kotak, harga setup ditetapkan terus oleh pasukan teknikal.\n\n"
            f"* Nota: Semua pakej menikmati langganan bulanan standard sebanyak RM{self.monthly_subscription_fee:.2f}/bulan yang merangkumi {self.free_chat_tokens} Chat Tokens percuma."
        )
        return guide

    def process_incoming_whatsapp_message(self, sender_phone: str, message_text: str) -> str:
        """Memproses mesej masuk dengan menghantarnya ke LEEABrain atau mod manual."""
        if not self.is_active:
            return "Sistem tidak aktif. Sila semak status langganan."

        if self.ai_mode:
            # Menghantar mesej kepada LEEABrain untuk dijana jawapan mengikut persona & SOP khas
            response = self.brain.generate_response(message_text)
            self.used_chat_tokens += 1
            return response
        else:
            return f"[HUMAN TOUCH] Mesej daripada {sender_phone} dialihkan kepada pegawai bertugas secara manual."

    def toggle_mode(self) -> str:
        """Menukar mod antara AI Auto-Pilot (LEEABrain) dan Human Touch secara real-time."""
        self.ai_mode = not self.ai_mode
        current_mode = "AI Auto-Pilot (LEEABrain)" if self.ai_mode else "Human Touch"
        return f"Mod pertukaran berjaya: Sistem kini berada dalam mod {current_mode}."

# --- CONTOH PENGGUNAAN ENJIN, DASHBOARD & LEEABRAIN ---
if __name__ == "__main__":
    leea = LEEASystemEngine(client_name="architech", package_type="Pro")
    
    print("=== PROFIL & STRUKTUR PAKEJ SISTEM ===")
    import json
    print(json.dumps(leea.get_system_profile(), indent=4, ensure_ascii=False))
    
    print("\n" + leea.get_subscription_and_setup_guide())
    
    print("\n=== PAPARAN DASHBOARD PELANGGAN ===")
    print(json.dumps(leea.get_client_dashboard(), indent=4, ensure_ascii=False))
    
    print("\n=== SIMULASI MESEJ MASUK MELALUI LEEABRAIN ===")
    incoming_msg = "Berapa harga pakej Pro?"
    reply = leea.process_incoming_whatsapp_message("+60183172114", incoming_msg)
    print(f"Mesej Masuk: {incoming_msg}")
    print(f"Respons: {reply}")