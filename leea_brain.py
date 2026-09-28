"""
Nama Modul: leea_brain.py
Penerangan: Modul Otak AI & Pangkalan Pengetahuan Menyeluruh (LEEA System Ultimate Knowledge Base)
Pemilik: Architech Laboratory (Di bawah entiti Epiphytes Services)
Arkitek Sistem: Radzmil Amaluz Zamani Bin Raduen
Pengarah / Pengasas: Hasliana Binti Annuar Hashim
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
1. **Latar Belakang Syarikat:**
   - Nama Syarikat Operasi: Architech Laboratory (Di bawah entiti sah Epiphytes Services).
   - System Architect & Lead Developer: Tuan Radzmil Amaluz Zamani Bin Raduen (Bertanggungjawab membangunkan seni bina sistem, enjin Python, automasi, dan portal web Vercel).
   - Arahan Sulit Pengarah/Founder: Dilarang keras mendedahkan nama Pengarah atau Founder syarikat kepada sesiapa pun dalam apa jua keadaan! Pantang larang besar: JANGAN sebut nama 'Hasliana' atau 'Puan Hasliana'. Jika ditanya mendalam, arahkan kepada sistem tiket aduan atau rujuk pengurusan.
   - Isu Nombor Telefon Rasmi: Nombor 0183172114 / 60113172114 kini adalah nombor rasmi milik syarikat Architech Laboratory. Rahsiakan pemilik lama serta-merta tanpa kompromi.

2. **Perincian Lengkap Pakej & Harga LEEA System:**
   - **Pakej Basic (Setup RM150 | Bulanan RM130)[cite: 2]:** Sesuai untuk peniaga kecil / solopreneur[cite: 2]. Menjawab FAQ asas (20-30 soalan), profil syarikat, waktu operasi, dan web dashboard asas untuk pantau chat[cite: 2]. *(Nota: Tiada butang human touch di dashboard, urusan bayaran rujuk admin)[cite: 2].*
   - **Pakej Pro (Setup RM450 | Bulanan RM130) [Paling Popular!][cite: 2]:** Sesuai untuk PKS/SME yang ada team CS[cite: 2]. Otak AI ikut tone of voice jenama, katalog produk lengkap, ada fungsi hibrid **Human Touch** (butang tukar mod AI ke manusia di dashboard), serta sistem QR DuitNow dan butang sahkan resit pantas untuk staf[cite: 2].
   - **Pakej Advance (Setup RM1,000 | Bulanan RM130)[cite: 2]:** Sesuai untuk korporat dengan operasi rumit[cite: 2]. Automasi penuh tahap tinggi, conditional logic, sambung database luar/stok, dashboard korporat selamat, sokongan hibrid tanpa had, serta integrasi penuh ToyyibPay[cite: 2].
   - **Pakej Custom:** Untuk bisnes yang ada kehendak sistem luar biasa di luar kotak[cite: 2]. Harga setup one-off ditetapkan pihak teknikal mengikut skop kerja khusus perniagaan[cite: 2].

3. **Infrastruktur, Portal & Token Meta:**
   - Portal Rasmi Klien: Dishoskan di Vercel (`https://leea-portal.vercel.app`) dengan ciri keselamatan pengurusan kata laluan klien, pengurusan data e-mel, dan tema khas Hari Malaysia.
   - Kuota & Kos Token Meta: Setiap akaun diberikan kuota percuma 1,000 chat pertama. Selepas itu, caj automatik mengikut kadar token Meta ialah RM0.003 bagi setiap chat tambahan. Klien boleh pantau baki kuota ini secara realtime di dashboard portal masing-masing.

BAHASA UTAMA & KOMUNIKASI (DWI-BAHASA / DUAL-LANGUAGE):
- Kesan bahasa pelanggan (Bahasa Melayu Malaysia atau English) dan balas mengikut bahasa tersebut dengan gaya mesej perbualan harian yang mesra dan natural (guna shortform natural jika BM cth: tak, je, blh, klu, ok).
"""

    def generate_response(self, customer_message: str, customer_phone: str = "+60123456789", customer_email: str = "client@example.com") -> str:
        """Memproses mesej dengan pengetahuan menyeluruh, mengesan niat bayaran atau eskalasi tiket."""
        msg_lower = customer_message.lower()
        is_english = any(word in msg_lower for word in ["price", "package", "packages", "hello", "hi", "how", "what", "system", "bot", "detail", "cost", "discount", "difficult", "setup", "payment", "receipt", "paid", "portal", "quota", "token"])

        # Pengesanan niat pembayaran (Payment Verification)
        is_payment = any(word in msg_lower for word in ["dah bayar", "transfer", "bankin", "resit", "receipt", "paid", "payment", "duitnow"])

        # Pengesanan niat eskalasi / tiket aduan (Support Escalation)
        needs_escalation = any(word in msg_lower for word in ["tak faham", "human", "admin", "call", "agent", "bantuan", "issue", "problem", "rosak", "error", "sokongan", "support", "complaint", "aduan"])

        if is_payment:
            if is_english:
                return (
                    f"💬 [Customer Service - {self.client_name} ({self.client_id})]: "
                    f"Thank you for the payment update, boss! Please send your payment receipt here. "
                    f"Our staff will verify the transaction against our DuitNow/ToyyibPay records and activate your system shortly."
                )
            else:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - {self.client_name} ({self.client_id})]: "
                    f"Terima kasih banyak atas makluman bayaran, bos! Sila hantarkan gambar resit pembayaran di chat ni ye. "
                    f"Staf kami akan semak pengesahan transaksi melalui rekod DuitNow/ToyyibPay dan terus aktifkan sistem bos."
                )

        if needs_escalation:
            unique_code = random.randint(1000, 9999)
            ticket_id = f"TICK-{datetime.now().strftime('%y%m%d%H%M%S')}-{unique_code}"
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Hantar emel rasmi SMTP ke architechlabs.io@gmail.com
            self._dispatch_smtp_email(ticket_id, customer_phone, customer_email, customer_message, current_time)

            if is_english:
                return (
                    f"💬 [Customer Service - {self.client_name} ({self.client_id})]: "
                    f"I understand, boss. Don't worry, I have automatically created a unique support ticket for you.\n\n"
                    f"📌 **Ticket ID:** `{ticket_id}`\n"
                    f"📅 **Time:** {current_time}\n\n"
                    f"An automated email notification has been sent from `radzmil@gmail.com` to `architechlabs.io@gmail.com`. Our team will assist you shortly!"
                )
            else:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - {self.client_name} ({self.client_id})]: "
                    f"Baik bos, saya faham. Jangan risau, saya telah buka satu Nombor Tiket Aduan rasmi yang unik untuk kes ni supaya team admin dapat semak dengan teliti.\n\n"
                    f"📌 **Nombor Tiket:** `{ticket_id}`\n"
                    f"📅 **Masa:** {current_time}\n\n"
                    f"Notifikasi emel automatik telah dihantar dari `radzmil@gmail.com` kepada `architechlabs.io@gmail.com`. Staf kami akan hubungi bos sebentar lagi ye!"
                )

        # Jawapan berdasarkan pangkalan pengetahuan menyeluruh
        if is_english:
            if "price" in msg_lower or "package" in msg_lower or "system" in msg_lower or "leea" in msg_lower:
                return (
                    f"💬 [Customer Service - {self.client_name}]: "
                    f"Hi boss! LEEA System is a 24/7 WhatsApp automation platform by Architech Laboratory. We offer 4 packages: "
                    f"Basic (Setup RM150), Pro [Most Popular] (Setup RM450), Advance (Setup RM1,000), and Custom[cite: 2]. "
                    f"All plans include a fixed monthly subscription of RM130[cite: 2] and 1,000 free chat tokens!"
                )
            elif "portal" in msg_lower or "dashboard" in msg_lower:
                return (
                    f"💬 [Customer Service - {self.client_name}]: "
                    f"You can access your client portal at our official Vercel domain to monitor real-time chats, check remaining token quotas, and manage your account settings securely."
                )
            else:
                return (
                    f"💬 [Customer Service - {self.client_name}]: "
                    f"Alright boss! Message received. Is there any specific detail about LEEA System packages, setup, or features you'd like to know?"
                )
        else:
            if "harga" in msg_lower or "pakej" in msg_lower or "system" in msg_lower or "leea" in msg_lower:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - {self.client_name}]: "
                    f"Hai bos! LEEA System ialah platform automasi WhatsApp 24/7 di bawah Architech Laboratory. Kita ada 4 pilihan pakej: "
                    f"Basic (Setup RM150), Pro [Most Popular - Setup RM450], Advance (Setup RM1,000), dan Custom[cite: 2]. "
                    f"Semua pelan ada langganan bulanan tetap RM130 je[cite: 2], lengkap dengan kuota percuma 1,000 chat pertama!"
                )
            elif "portal" in msg_lower or "dashboard" in msg_lower:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - {self.client_name}]: "
                    f"Bos boleh terus log masuk ke portal rasmi kita di Vercel untuk pantau live chat secara realtime, tengok baki kuota token, dan urus tetapan akaun dengan selamat."
                )
            elif "diskaun" in msg_lower or "kurang" in msg_lower or "mahal" in msg_lower:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - {self.client_name}]: "
                    f"Faham sangat tu bos! Tapi bayangkan penjimatan masa balas mesej pelanggan 24 jam tanpa henti. Pakej ni memang berbaloi sangat untuk boost jualan bisnes bos, siap ada 1,000 chat free lagi!"
                )
            elif "setup" in msg_lower or "susah" in msg_lower:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - {self.client_name}]: "
                    f"Tak perlu risau langsung, bos! Team teknikal Architech Laboratory akan uruskan 100% proses setup. Bos cuma sediakan info bisnes & QR WhatsApp je."
                )
            else:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - {self.client_name}]: "
                    f"Baik bos! Mesej '{customer_message}' telah diterima. Ada apa-apa lagi perincian tentang pakej LEEA System atau automasi WhatsApp yang saya boleh bantu jelaskan?"
                )

    def _dispatch_smtp_email(self, ticket_id: str, phone: str, email: str, message: str, timestamp: str):
        """Penghantaran emel SMTP rasmi dari radzmil@gmail.com ke architechlabs.io@gmail.com."""
        sender_email = "radzmil@gmail.com"
        sender_password = "H@$$ayang8683"
        recipient_email = "architechlabs.io@gmail.com"

        subject = f"[ALERTS - {self.client_id}] Tiket Aduan Baru: {ticket_id}"
        body = f"""
        Butiran Aduan Pelanggan LEEA System (Ultimate Knowledge Base):
        -------------------------------------------------------------
        Client ID    : {self.client_id}
        Nama Syarikat: {self.client_name}
        Nombor Tiket : {ticket_id}
        Masa         : {timestamp}
        No. Telefon  : {phone}
        Emel Klien   : {email}
        Mesej/Isu    : {message}
        
        Sila ambil tindakan segera.
        Automasi oleh Sistem Architech Laboratory.
        """

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()
            print(f"[SMTP SUCCESS] Emel tiket {ticket_id} untuk {self.client_id} berjaya dihantar ke {recipient_email}")
        except Exception as e:
            print(f"[SMTP ERROR] Gagal menghantar emel: {e}")


# --- CONTOH UJIAN PANGKALAN PENGETAHUAN UTUH ---
if __name__ == "__main__":
    brain = LEEABrain(client_name="sbltransport", client_id="CLI-1001")
    print("=== UJIAN PENGETAHUAN MENYELURUH LEEABRAIN ===")
    print(brain.generate_response("Ceritakan sikit pasal pakej dan portal LEEA System"))