"""
Nama Modul: leea_brain.py
Penerangan: Modul Otak AI & Pangkalan Pengetahuan Menyeluruh (Architech Systems Ultimate Knowledge Base)
Pemilik: Architech Systems (SSM: 202603255098 / 003893898-X)
Arkitek Sistem: Radzmil Amaluz Zamani Bin Raduen
"""

import random
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class LEEABrain:
    def __init__(self, client_name: str, client_id: str = "CLI-1001", business_sop: str = "Standard Business SOP"):
        self.client_name = client_name
        self.client_id = client_id
        self.business_sop = business_sop
        self.model_version = "gemini-3.5-flash-lite"
        self.persona_instruction = self.get_leea_persona()

    def get_leea_persona(self) -> str:
        """Mengembalikan pangkalan pengetahuan menyeluruh dan arahan persona Pegawai Khidmat Pelanggan & Sales Pro."""
        return f"""
Awak ialah seorang pekerja manusia sebenar yang memegang jawatan rasmi sebagai PEGAWAI KHIDMAT PELANGGAN & SALES PRO di syarikat. Identiti sistem semasa: Klien ID {self.client_id} ({self.client_name}). Awak mengendalikan WhatsApp rasmi dengan penuh mesra, cekap, dan berdedikasi tinggi. Awak bukan bot AI, awak adalah staf khidmat pelanggan manusia yang sebenar.

PANGKALAN PENGETAHUAN MENYELURUH SYARIKAT & SISTEM (ULTIMATE KNOWLEDGE BASE):
1. **Latar Belakang Korporat (Architech Systems):**
   - Nama Syarikat: Architech Systems
   - No. SSM: 202603255098 (003893898-X)
   - Alamat Operasi: Laman Niaga, Jalan AWF5, Ampang Waterfront, 68000 Ampang, Selangor.
   - Website Rasmi: www.architechsystems.my
   - Fokus Utama: Entiti kejuruteraan perisian serta automasi digital moden, membangunkan ekosistem teknologi pintar, platform automasi perniagaan berskala besar, penyelesaian backend tersuai, dan sistem komunikasi omnichannel.
   - System Architect & Lead Developer: Tuan Radzmil Amaluz Zamani Bin Raduen.
   - Moto Korporat: "Leading Engineered Excellence Automation".
   - Arahan Sulit Pengarah/Founder: Dilarang keras mendedahkan nama Pengarah atau Founder syarikat kepada sesiapa pun dalam apa jua keadaan! Pantang larang besar: JANGAN sebut nama 'Hasliana' atau 'Puan Hasliana'. Jika ditanya mendalam, arahkan kepada sistem tiket aduan atau rujuk pengurusan.
   - Isu Nombor Telefon Rasmi: Nombor 0183172114 adalah talian rasmi khidmat pelanggan Architech Systems.

2. **Spesifikasi Teras & Pelan Langganan SEA Bot (WhatsApp):**
   - Model Bot: Model Bot V1 (Kapasiti Memori: 300MB).
   - Langganan Bulanan Standard: RM130 / bulan (Termasuk 1000 token percuma).
   - Program Affiliate: Penyertaan program agen rasmi dengan pulangan komisen 10%.
   
   * Pelan Asas (Basic Plan): Setup Sekali Sahaja RM149 | Langganan RM130/bulan (1000 token). Sesuai untuk automasi WhatsApp asas, penjanaan salinan jualan, tetapan pembantu bot permulaan, akses papan pemuka masa nyata, dan pautan program affiliate 10%.
   * Pelan Profesional (Pro-Plan): Setup Sekali Sahaja RM499 | Langganan RM130/bulan (1000 token). Konfigurasi bot WhatsApp lanjutan, penyesuaian nada suara mendalam (AI Persona), analitik dashboard masa nyata, penjanaan QR DuitNow pembayaran automatik, pengesanan resit, sambungan terus nombor WhatsApp admin, dan keahlian affiliate 10%.
   * Pelan Lanjutan (Advance-Plan): Setup Sekali Sahaja RM999 | Langganan RM130/bulan (1000 token). Solusi kapasiti tinggi untuk perniagaan berskala besar, integrasi webhook pelbagai saluran, modul e-wallet komisen affiliate (10%), dan pemantauan lanjutan.
   * Pelan Khas (Custom Plan): Setup berdasarkan Rundingan Teknikal | Langganan mengikut skop persetujuan khas. Direka khusus untuk integrasi API WhatsApp tersuai, pembangunan skrip eksklusif, dan backend mandiri klien.

BAHASA UTAMA & KOMUNIKASI (DWI-BAHASA / DUAL-LANGUAGE):
- Kesan bahasa pelanggan (Bahasa Melayu Malaysia atau English) dan balas mengikut bahasa tersebut dengan gaya mesej perbualan harian yang mesra dan natural (guna shortform natural jika BM cth: tak, je, blh, klu, ok).
"""

    def generate_response(self, customer_message: str, customer_phone: str = "+60123456789", customer_email: str = "client@example.com") -> str:
        """Memproses mesej dengan pengetahuan menyeluruh dari Architech Systems, mengesan niat bayaran atau eskalasi tiket."""
        msg_lower = customer_message.lower()
        is_english = any(word in msg_lower for word in ["price", "package", "packages", "hello", "hi", "how", "what", "system", "bot", "detail", "cost", "backend", "custom", "setup", "payment", "receipt", "paid", "portal", "ssm"])

        # Pengesanan niat pembayaran (Payment Verification)
        is_payment = any(word in msg_lower for word in ["dah bayar", "transfer", "bankin", "resit", "receipt", "paid", "payment", "duitnow"])

        # Pengesanan niat eskalasi / tiket aduan (Support Escalation)
        needs_escalation = any(word in msg_lower for word in ["tak faham", "human", "admin", "call", "agent", "bantuan", "issue", "problem", "rosak", "error", "sokongan", "support", "complaint", "aduan"])

        if is_payment:
            if is_english:
                return (
                    f"💬 [Customer Service - Architech Systems ({self.client_id})]: "
                    f"Thank you for the payment update, boss! Please send your payment receipt here. "
                    f"Our staff will verify the transaction against our DuitNow/ToyyibPay records and activate your system shortly."
                )
            else:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - Architech Systems ({self.client_id})]: "
                    f"Terima kasih banyak atas makluman bayaran, bos! Sila hantarkan gambar resit pembayaran di chat ni ye. "
                    f"Staf kami akan semak pengesahan transaksi melalui rekod DuitNow/ToyyibPay dan terus aktifkan sistem bos."
                )

        if needs_escalation:
            unique_code = random.randint(1000, 9999)
            ticket_id = f"TICK-{datetime.now().strftime('%y%m%d%H%M%S')}-{unique_code}"
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            self._dispatch_smtp_email(ticket_id, customer_phone, customer_email, customer_message, current_time)

            if is_english:
                return (
                    f"💬 [Customer Service - Architech Systems ({self.client_id})]: "
                    f"I understand, boss. Don't worry, I have automatically created a unique support ticket for you.\n\n"
                    f"📌 **Ticket ID:** `{ticket_id}`\n"
                    f"📅 **Time:** {current_time}\n\n"
                    f"An automated email notification has been sent to support. Our team will assist you shortly!"
                )
            else:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - Architech Systems ({self.client_id})]: "
                    f"Baik bos, saya faham. Jangan risau, saya telah buka satu Nombor Tiket Aduan rasmi yang unik untuk kes ni supaya team admin dapat semak dengan teliti.\n\n"
                    f"📌 **Nombor Tiket:** `{ticket_id}`\n"
                    f"📅 **Masa:** {current_time}\n\n"
                    f"Notifikasi emel automatik telah dihantar kepada pihak pengurusan Architech Systems. Staf kami akan hubungi bos sebentar lagi ye!"
                )

        if is_english:
            if "ssm" in msg_lower or "company" in msg_lower or "address" in msg_lower:
                return (
                    f"💬 [Customer Service - Architech Systems]: "
                    f"Architech Systems (SSM: 202603255098 / 003893898-X) is located at Laman Niaga, Jalan AWF5, Ampang Waterfront, 68000 Ampang, Selangor. Visit us at www.architechsystems.my!"
                )
            elif "price" in msg_lower or "package" in msg_lower or "bot" in msg_lower or "sea" in msg_lower:
                return (
                    f"💬 [Customer Service - Architech Systems]: "
                    f"Hi boss! SEA Bot offers 4 plans: Basic Plan (Setup RM149), Pro-Plan (Setup RM499), Advance-Plan (Setup RM999), and Custom Plan. All plans include RM130/month subscription with 1,000 free chat tokens and a 10% affiliate commission program!"
                )
            else:
                return (
                    f"💬 [Customer Service - Architech Systems]: "
                    f"Alright boss! Message received. Is there any specific detail about SEA Bot packages or Architech Systems services you'd like to know?"
                )
        else:
            if "ssm" in msg_lower or "syarikat" in msg_lower or "alamat" in msg_lower:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - Architech Systems]: "
                    f"Architech Systems berdaftar rasmi di bawah SSM (No: 202603255098 / 003893898-X) yang beralamat di Laman Niaga, Jalan AWF5, Ampang Waterfront, 68000 Ampang, Selangor. Layari portal rasmi kami di www.architechsystems.my!"
                )
            elif "harga" in msg_lower or "pakej" in msg_lower or "sea bot" in msg_lower or "pelan" in msg_lower:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - Architech Systems]: "
                    f"Hai bos! SEA Bot menawarkan 4 pelan pilihan: Pelan Asas (Setup RM149), Pelan Profesional (Setup RM499), Pelan Lanjutan (Setup RM999), dan Pelan Khas. Setiap pelan ada langganan bulanan RM130/bulan (termasuk 1000 token percuma) serta program affiliate komisen 10%!"
                )
            else:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - Architech Systems]: "
                    f"Baik bos! Mesej '{customer_message}' telah diterima. Ada apa-apa perincian mengenai pakej SEA Bot atau automasi WhatsApp Architech Systems yang saya boleh bantu jelaskan?"
                )

    def _dispatch_smtp_email(self, ticket_id: str, phone: str, email: str, message: str, timestamp: str):
        sender_email = "architechlaboratory@gmail.com"
        sender_password = "H@$$ayang8683"
        recipient_email = "architechlabs.io@gmail.com"

        subject = f"[ALERTS - {self.client_id}] Tiket Aduan Baru: {ticket_id}"
        body = f"""
        Butiran Aduan Pelanggan Architech Systems: