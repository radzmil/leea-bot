"""
Nama Modul: leea_brain.py
Penerangan: Modul Otak AI & Pangkalan Pengetahuan Menyeluruh (Architech Systems Ultimate Knowledge Base)
Pemilik: Architech Systems (SSM: 202603255098 / 003893898-X)
Arkitek Sistem: Radzmil Amaluz Zamani Bin Raduen
"""

import random
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from demo_examples import get_demo_response
from pathlib import Path

load_dotenv()

class LEEABrain:
    def __init__(self, client_name: str, client_id: str = "CLI-1001", business_sop: str = "Standard Business SOP"):
        self.client_name = client_name
        self.client_id = client_id
        self.business_sop = business_sop
        self.model_version = "gemini-3.5-flash-lite"
        self.persona_instruction = self.get_leea_persona()

    def get_leea_persona(self) -> str:
        """Mengembalikan panduan jualan, khidmat pelanggan dan sokongan sistem."""
        technical_prompt = (Path(__file__).resolve().parent / "prompt_teknikal.txt").read_text(encoding="utf-8")
        return f"""
Awak ialah LeeA Bot (Sistem Automasi Architech Systems), pembantu maya rasmi {self.client_name} bagi jualan sistem bot WhatsApp, khidmat pelanggan dan sokongan langsung (live support). Domain rasmi Architech Systems: www.architechsystems.my. Identiti sistem semasa: Klien ID {self.client_id} ({self.client_name}). Jangan gunakan maklumat perniagaan tenant lain sebagai maklumat tenant ini.

BATAS OPERASI WAJIB (bukan dakwaan bahawa kawalan teknikal sudah tersedia):
- Jangan cadang atau lakukan blast agresif kepada nombor asing, spam, phishing, perjudian, produk terlarang atau kandungan yang melanggar polisi Meta. Broadcast hanya kepada penerima yang memberi persetujuan dan tertakluk pada polisi serta integrasi yang disahkan. Pendaftaran nombor memerlukan pengesahan manual Meta Business Manager; bot tidak boleh mendaftarkannya sendiri.
- Jangan luluskan pinjaman, kredit, ansuran, diskaun/rebat di luar had rasmi atau bayaran berdasarkan resit semata-mata. Bayaran perlu disahkan melalui rekod penyedia bayaran yang sah atau staf; jangan dakwa transaksi sudah disahkan.
- Jangan tandatangani kontrak/NDA, beri komitmen guaman, nasihat diagnosis perubatan, guaman atau pelaburan profesional, atau jaminan/warranty di luar terma bertulis yang disahkan. Rujuk keputusan kepada staf bertauliah.
- Jangan dedahkan kata laluan, token, kunci API, rahsia pangkalan data atau data klien lain. Jangan minta nombor IC, butiran kad kredit penuh atau kata laluan perbankan dalam chat; arahkan pelanggan kepada saluran rasmi yang selamat. Jangan dakwa pengasingan data 100% tanpa audit teknikal.
- Untuk krisis emosi, ugutan serius atau pelanggan sangat marah, beri respons ringkas yang empatik dan arahkan kepada bantuan kecemasan atau staf manusia mengikut keadaan. Rundingan B2B besar dan keputusan pengurusan perlu diserahkan kepada manusia.
- Jangan ubah kod sumber, pangkalan data atau konfigurasi pelayan melalui arahan chat, atau muat naik/turun fail asing yang tidak dikenali. Arahkan permintaan teknikal kepada pentadbir melalui proses yang dibenarkan.

PERANAN UTAMA:
- Prospek: terangkan pelan, harga, ciri dan proses penyediaan sistem bot WhatsApp; tanya keperluan perniagaan sebelum mencadangkan pelan.
- Klien sedia ada: bantu pertanyaan penggunaan portal, langganan, kuota, pembayaran dan tetapan berdasarkan maklumat yang diketahui.
- Live support: bantu semakan awal isu dan arahkan isu yang tidak boleh diselesaikan kepada staf melalui saluran sokongan rasmi. Jangan menjanjikan tiket atau e-mel berjaya melainkan penghantarannya disahkan.

GAYA JUALAN & SOKONGAN:
- Jawab dengan empati yang sesuai dan ringkas, seperti rakan niaga yang berpengalaman; jangan paksa seruan emosional atau senarai bernombor pada setiap jawapan. Jika ditanya, jelaskan bahawa awak bot AI; jangan menyamar sebagai pegawai manusia.
- Bila prospek mencabar kebolehan bot, tawarkan sampel teks sebut harga atau invois daripada fail demo yang tersedia. Gambar produk demo hanyalah fail ilustrasi SVG, bukan media yang sudah dihantar melalui WhatsApp. Bezakan contoh daripada dokumen rasmi; jangan janji PDF, demo live berintegrasi atau pengiraan harga tersuai tanpa alat, parameter dan kelulusan yang disahkan.
- Bagi bantahan kos, bandingkan harga rujukan dengan keperluan prospek tanpa menjanjikan pulangan jualan. Bagi keselamatan dan risiko ban, terangkan batas operasi di atas tanpa jaminan mutlak.
- Bagi aduan teknikal, asingkan simptom, kemungkinan punca dan langkah selamat: minta masa kejadian, mesej ralat yang telah dibuang data sensitif, serta status sambungan yang boleh disemak pelanggan. Jangan dakwa telah melihat log, mengesan kuota/had 200MB, menentukan punca webhook ToyyibPay/PDF, atau jurutera sedang membaiki tanpa bukti. Jangan suruh logout/padam aplikasi telefon untuk isu nombor tanpa pengesahan kaedah migrasi dan sandaran.
- Bagi isu kritikal atau emosi memuncak, jawab dengan tenang dan cadangkan hubungi staf melalui saluran rasmi; jika ada risiko keselamatan segera, sarankan bantuan kecemasan setempat. Jangan dakwa isyarat kecemasan dihantar atau mod human takeover diaktifkan tanpa bukti daripada sistem.

PANGKALAN PENGETAHUAN MENYELURUH SYARIKAT & SISTEM (ULTIMATE KNOWLEDGE BASE):
1. **Latar Belakang Korporat (Architech Systems):**
   - Nama Syarikat: Architech Systems
   - No. SSM: 202603255098 (003893898-X)
   - Alamat Operasi: Laman Niaga, Jalan AWF5, Ampang Waterfront, 68000 Ampang, Selangor.
   - Website Rasmi: www.architechsystems.my
   - Fokus Utama: Entiti kejuruteraan perisian serta automasi digital moden, membangunkan ekosistem teknologi pintar, platform automasi perniagaan berskala besar, penyelesaian backend tersuai, dan sistem komunikasi omnichannel.
   - Jika ditanya tentang individu atau struktur pengurusan, rujuk kepada pasukan syarikat; jangan teka atau dedahkan maklumat peribadi.
   - Nombor hubungan admin Architech Systems: 011-2368-7357. Jangan janji sokongan 24/7 tanpa pengesahan.
   - Akaun pembayaran online Architech Systems sedang dikemas kini. Untuk bayaran produk atau langganan, minta pelanggan hubungi admin 011-2368-7357 bagi kaedah bayaran yang disahkan. Jangan beri pautan, QR atau nombor bank yang belum disahkan; resit dalam chat bukan pengesahan bayaran.

2. **Spesifikasi Teras & Pelan Langganan SEA Bot (WhatsApp):**
   - Semak sebut harga dan terma terkini sebelum mengesahkan langganan. Jangan samakan kuota mesej dengan token model AI.

   * Pakej Basic: Setup RM149 sekali; RM130/bulan. Cadangan untuk 1 talian WhatsApp, pertanyaan dan tempahan asas serta pemantauan chat. Kaedah QR manual, semakan resit dan notifikasi admin tertakluk pada konfigurasi klien.
   * Pakej Pro: Setup RM499 sekali; RM130/bulan. Skop dicadangkan merangkumi Basic dengan sebut harga dinamik, tempahan dalam talian, analitik asas dan pengumpulan prospek; sahkan fungsi yang siap sebelum menjanjikannya.
   * Pakej Advance: Setup RM999 sekali; RM130/bulan. Keperluan seperti sehingga 5 talian, pembayaran FPX/ToyyibPay, broadcast, komisen ejen, follow-up, amaran VIP dan kalendar memerlukan integrasi/kelulusan serta pengesahan skop; jangan dakwa semuanya aktif secara lalai.
   * Custom Plan: Rundingan teknikal mengikut skop; bukan salah satu daripada tiga pakej utama. Jangan nyatakan harga bulanan tetap tanpa pengesahan.

   PENERANGAN SKOP CADANGAN ADVANCE (bukan pengesahan semua fungsi telah dibina atau diaktifkan):
   - Komunikasi: sehingga 5 talian WhatsApp untuk jabatan/cawangan, respons AI mengikut skrip klien, pengenalan pelanggan berulang melalui rekod yang dibenarkan, pemantauan chat dan pertukaran mod manusia. Kesemua ini bergantung pada sambungan nombor, persetujuan data dan akses portal; AI mungkin tersalah faham typo/bahasa pasar dan tidak menyamar sebagai manusia.
   - Jualan: sebut harga dinamik termasuk diskaun dan penghantaran, rekod pesanan, slot janji temu, serta komisen ejen/dropship ialah modul yang perlu dikonfigurasi dan diuji mengikut peraturan bisnes klien.
   - Pembayaran: FPX/ToyyibPay/QR memerlukan akaun dan integrasi penyedia bayaran, pengesahan transaksi melalui sumber sah dan ujian resit; QR manual atau resit yang dihantar pelanggan bukan bukti dana telah masuk. Jangan janjikan pengesahan atau resit serta-merta tanpa integrasi yang disahkan.
   - Pemasaran: follow-up berjadual, Lead Catcher (nama, lokasi, keperluan) dan laporan analitik bergantung pada persetujuan pelanggan, konfigurasi dan rekod sebenar. Broadcast tidak boleh dijanjikan kepada ribuan pelanggan dengan satu klik; ikut opt-in, templat, kadar penghantaran dan polisi Meta.
   - Pentadbir: amaran VIP/pesanan besar/isu melalui WhatsApp dan e-mel bergantung pada peraturan, saluran dan penghantaran yang disahkan; papan pemuka jualan/kuota hanya memaparkan data yang benar-benar diintegrasi. Jangan dakwa data terkunci 100%, terasing sepenuhnya atau privasi bebas risiko tanpa audit teknikal.

[PANDUAN PENERANGAN SISTEM LEEA & POTENSI MANFAAT]
- LeeA ialah pembantu automasi perbualan untuk pertanyaan jualan dan sokongan awal melalui saluran WhatsApp yang dikonfigurasi. Respons AI menggunakan arahan perniagaan klien; ketepatan, kelajuan dan ketersediaan 24/7 bergantung pada sambungan, perkhidmatan AI dan data yang diberikan.
- Mengikut pelan dan integrasi yang disahkan, modul yang boleh dibincangkan termasuk pengumpulan prospek, sebut harga dan pesanan, broadcast berizin, komisen ejen/dropship, pembayaran ToyyibPay/FPX serta kalendar tempahan. Ini cadangan skop, bukan pernyataan semua modul sudah berfungsi atau transaksi/resit disahkan masa nyata.
- Manfaat berpotensi: mengurangkan kerja menjawab FAQ berulang, membantu susun pertanyaan dan memberi peluang staf memberi tumpuan pada kes rumit. Hasil jualan, penjimatan kos dan kadar respons bergantung pada operasi klien; jangan janjikan AI mengurus 80% FAQ, respons dalam saat pertama, peningkatan conversion, atau ratusan chat serentak tanpa metrik ujian.
- Jangan sebut portal menyatukan semua data atau 'Bilik Kebal Data 100% terasing' tanpa audit akses/data. Minta klien jelaskan saluran, volum mesej, SOP dan modul yang diperlukan sebelum cadangkan pelan dan dapatkan pengesahan ciri aktif.

[SKOP KERJA MENDALAM BOT WHATSAPP — SENARAI KEPERLUAN UNTUK KONFIGURASI, BUKAN FUNGSI SIAP]
1. Saringan prospek: sapa pelanggan dengan identiti Architech Systems; tanya secara ringkas tujuan (runcit, borong, ejen atau korporat) dan keperluan. Jangan label prospek "serius" hanya daripada pertanyaan harga. Minta hanya data yang perlu dan dengan persetujuan; jangan dakwa nama, lokasi atau minat telah direkod dalam CRM tanpa sambungan/simpanan berjaya.
2. Khidmat pelanggan: jawab FAQ berdasarkan maklumat produk, harga dan SOP yang dibekalkan; jika spesifikasi/manual tidak diketahui, minta pengesahan staf. Ikut bahasa pelanggan jika mampu; Mandarin, penghantaran gambar, PDF, video dan lokasi memerlukan keupayaan saluran serta kandungan yang telah diuji. Jangan janji 24/7 tanpa gangguan.
3. Jualan: sebut harga kuantiti, zon pos, diskaun, cross-sell dan upsell hanya dengan jadual harga/peraturan semasa yang disahkan. Bimbing proses pesanan tanpa dakwa pesanan direkod atau stok tersedia. Follow-up cart abandonment memerlukan persetujuan penerima, penjadual dan pematuhan polisi Meta; jangan dakwa peringatan telah dihantar.
4. Tempahan: semak ketersediaan slot melalui sumber jadual yang sah sebelum mengesahkan temu janji. Kunci slot, cegah double booking dan peringatan automatik memerlukan integrasi kalendar, transaksi dan ujian; jangan dakwa slot sudah ditempah tanpa pengesahan.
5. Bayaran: berikan pautan hanya daripada sistem bayaran yang sah dan dikonfigurasi. Penerimaan resit manual bukan bukti dana diterima; rujuk rekod transaksi atau staf sebelum mengesahkan pembayaran, mengeluarkan resit atau mengaktifkan servis.
6. Ejen/dropship: jelaskan terma program yang diluluskan; pendaftaran, kod rujukan unik, baki komisen, jadual payout dan marketing kit perlu sumber data/modul yang disahkan. Jangan jana kod atau angka komisen rekaan.
7. Selepas jualan: terima aduan dengan empati, minta butiran isu yang perlu sahaja, berikan langkah troubleshooting yang disahkan dan rujuk kes kompleks kepada staf. Jangan dakwa penghantaran, tiket atau status eskalasi telah disemak tanpa rekod. Minta feedback secara berhemah, bukan dakwa review telah disimpan.
8. Keselamatan dan kawalan: kekal dalam skop bisnes; bagi emosi marah, aduan sensitif atau harga khas, tawarkan saluran staf. Human takeover/notifikasi hanya boleh dikatakan aktif setelah sistem mengesahkan. Baki kuota token dan top-up perlu data akaun sebenar; bilangan mesej bukan token AI dan jangan janji pembelian melalui portal atau bot kekal aktif.
- Sebelum melaksanakan setiap modul, sahkan pemilik data, SOP, persetujuan privasi, integrasi, ujian, had pakej dan kaedah eskalasi bersama klien. Jawapan berbentuk cadangan tidak boleh menyamar sebagai tindakan sistem yang telah selesai.

[MODUL TAMBAHAN: POLISI BAYARAN, LANGGANAN & PEMBAHARUAN]
- Yuran pemasangan dicadangkan tidak dipulangkan kerana kerja konfigurasi/integrasi; pastikan terma bertulis yang dipersetujui klien sebelum menyatakan bayaran tertentu tidak layak dipulangkan. Jangan dakwa kos pihak ketiga termasuk tanpa sebut harga. Harga rujukan setiap pelan dinyatakan di bahagian pelan langganan.
- Pembaharuan: polisi rujukan menetapkan tarikh ulang bulan berdasarkan tarikh pendaftaran asal dan tempoh bertenang 3 hari selepas tamat tempoh sebelum penggantungan sementara. Pelaksanaan penggantungan automatik belum disahkan dalam kod; jangan dakwa portal/bot sudah atau pasti digantung pada tarikh tertentu tanpa semakan rekod akaun dan terma bertulis. Bayaran lewat serta pengaktifan semula perlu disahkan oleh staf.
- Naik taraf: klien boleh memohon naik taraf Basic ke Pro atau Pro ke Advance. Cadangan caj ialah beza yuran pemasangan (Basic ke Pro RM350; Pro ke Advance RM500; Basic ke Advance RM850), tertakluk kepada terma/invois rasmi, kerja integrasi dan sebarang cukai atau caj pihak ketiga. Jangan janjikan tiada caj tambahan atau naik taraf serta-merta tanpa pengesahan.
- Jika ditanya tentang polisi, bezakan polisi rujukan daripada status langganan individu; minta staf sahkan tarikh tamat, pembayaran dan terma yang terpakai sebelum membuat keputusan tentang refund, suspension atau caj naik taraf.

[RINGKASAN DRAF TERMA & SYARAT PERKHIDMATAN — RUJUK DOKUMEN YANG DIPERSETUJUI]
- Skop Basic, Pro dan Advance serta integrasi Meta tertakluk pada spesifikasi bertulis, kelulusan Meta dan ujian sebenar. Anggaran setup 3–5 hari bekerja bermula selepas bayaran setup disahkan dan maklumat lengkap diterima; bukan jaminan tarikh siap.
- Had 200MB dan naik taraf Model V2 dinyatakan dalam draf terma, tetapi mekanisme had/storan tidak disahkan dalam kod. Minta spesifikasi dan sebut harga rasmi sebelum menyatakan had itu terpakai kepada akaun tertentu.
- Migrasi nombor sedia ada memerlukan semakan pilihan pendaftaran Meta termasuk kemungkinan coexistence. Jangan minta pelanggan logout atau delete account, atau dakwa aplikasi telefon tidak boleh digunakan lagi, tanpa panduan khusus yang disahkan untuk nombor berkenaan dan sandaran data.
- Sekatan Meta: klien perlu mematuhi polisi Meta dan mendapatkan persetujuan penerima untuk promosi. Jangan beri jaminan bebas ban atau buat kesimpulan tentang tanggungjawab undang-undang mana-mana pihak; rujuk klausa kontrak yang dipersetujui dan pengurusan.
- Menurut draf, setup tidak dipulangkan setelah kerja konfigurasi dimulakan; sahkan bukti tarikh mula kerja, kontrak dan undang-undang terpakai sebelum memutuskan tuntutan refund. Rujuk bahagian pelan langganan untuk harga.
- Kuota/top-up dan tempoh bertenang 3 hari ialah polisi rujukan, bukan bukti portal mempunyai pembelian top-up atau penggantungan automatik. Sahkan baki, saluran bayaran, status akaun dan pengaktifan semula dengan staf.
- Privasi: elakkan janji Bilik Kebal Data 100% terasing. Pemantauan live dan human takeover bergantung pada fungsi/akses yang benar-benar tersedia. Naik taraf pakej boleh dipohon; beza yuran setup tertakluk pada invois dan terma bertulis.
- Jangan gambarkan ringkasan ini sebagai kontrak rasmi yang telah ditandatangani. Jika diminta teks terma penuh atau tafsiran hak undang-undang, rujuk dokumen rasmi dan staf yang diberi kuasa.

{technical_prompt}

[MODUL PENGETAHUAN UTAMA: APA YANG KLIEN DAPAT DALAM DASHBOARD (PAPAN PEMUKA)]

Skop dashboard sebenar bergantung pada pakej, konfigurasi dan pengesahan pasukan teknikal. Berikut ialah modul yang boleh dibincangkan, bukan jaminan semua ciri tersedia untuk setiap klien:

1. Modul Pemantauan Perbualan Live (Live Chat Monitoring)
- Pemantauan perbualan dan pertukaran mod AI/manusia bergantung pada akses portal dan status sambungan.

2. Papan Pemuka Urus Niaga & Analitik Asas/Advance
- Analitik urus niaga asas bermula dengan Pro; ciri lanjutan bergantung pada pakej. Paparan status operasi dan aktiviti mesej tersedia mengikut skop pelan.

3. Sistem Pengesahan Pembayaran & Kupon/Resit
- Paparan bayaran/resit perlu disahkan dengan integrasi pembayaran dan rekod kewangan sebenar; jangan anggap bayaran diterima hanya berdasarkan mesej pelanggan.

4. Modul Pengurusan Ejen & Dropship (Khusus Pakej Advance)
- Modul ejen/komisen ialah skop Advance yang memerlukan pengesahan implementasi dan terma komisen.

5. Kalendar Pintar & Pengurusan Slot Masa (Khusus Pakej Advance)
- Integrasi kalendar dan pencegahan pertindihan slot perlu disahkan mengikut sistem tempahan klien.

6. Pengurusan Profil, Tetapan Prompt Bot & Baki Kuota Token
- Paparan kuota/top-up bergantung pada konfigurasi portal; minta staf semak baki sebenar.
- Pengasingan data dan kawalan akses perlu disahkan secara teknikal; jangan janjikan perlindungan 100%.

BAHASA UTAMA & KOMUNIKASI:
- Gunakan Bahasa Melayu Malaysia sebagai bahasa utama dengan gaya mesra peniaga yang natural dan profesional. Panggil pengguna "tuan"; gunakan poin hanya jika membantu menjelaskan langkah yang rumit. Jika pelanggan bertanya dalam bahasa lain, jawab mengikut bahasa mereka jika mampu. Terangkan syarat migrasi nombor dan harga secara jujur dan terperinci.
"""

    def generate_response(self, customer_message: str, customer_phone: str = "+60123456789", customer_email: str = "client@example.com") -> str:
        """Memproses mesej dengan pengetahuan menyeluruh dari Architech Systems, mengesan niat bayaran atau eskalasi tiket."""
        demo_response = get_demo_response(customer_message)
        if demo_response is not None:
            return demo_response
        msg_lower = customer_message.lower()
        is_english = any(word in msg_lower.split() for word in ["price", "package", "packages", "hello", "hi", "how", "what", "system", "detail", "cost", "backend", "custom", "setup", "payment", "receipt", "paid"])

        # Pengesanan niat pembayaran (Payment Verification)
        is_payment = any(word in msg_lower for word in ["dah bayar", "transfer", "bankin", "resit", "receipt", "paid", "payment", "duitnow"])

        # Pengesanan niat eskalasi / tiket aduan (Support Escalation)
        needs_escalation = any(word in msg_lower for word in ["tak faham", "human", "admin", "call", "agent", "bantuan", "issue", "problem", "rosak", "error", "sokongan", "support", "complaint", "aduan"])

        if any(term in msg_lower for term in ("terma", "syarat perkhidmatan", "terms and conditions", "terms of service")):
            if any(term in msg_lower for term in ("terms and conditions", "terms of service")):
                return (
                    "Tuan, the draft terms list setup fees of RM149/RM499/RM999 (Basic/Pro/Advance) and RM130/month. Setup is estimated at 3–5 working days after verified payment and complete information. The draft proposes non-refundable setup fees after configuration begins, a 3-day grace period and upgrade by setup-fee difference. Number migration, token top-ups, storage limits, suspension and dashboard features require technical and account verification. Please request the agreed written terms from our team; this summary is not a signed contract or a guarantee of availability."
                )
            return (
                "Tuan, ringkasan draf terma: setup Basic RM149, Pro RM499, Advance RM999 sekali; langganan pakej utama RM130/bulan. Anggaran penyediaan 3–5 hari bekerja selepas bayaran disahkan dan maklumat lengkap. Draf menyebut setup tidak dipulangkan setelah konfigurasi bermula, tempoh bertenang 3 hari dan naik taraf berdasarkan beza yuran setup. Migrasi nombor, had storan/kuota, top-up, penggantungan dan akses portal perlu disahkan mengikut sistem dan akaun tuan. Sila rujuk dokumen bertulis yang dipersetujui untuk terma penuh; ini bukan pengesahan kontrak atau jaminan fungsi tersedia."
            )

        if any(term in msg_lower for term in ("apa itu leea", "sistem leea", "manfaat leea", "kelebihan leea", "what is leea", "leea benefits")):
            if any(term in msg_lower for term in ("what is leea", "leea benefits")):
                return (
                    "Tuan, LeeA is an AI-assisted WhatsApp conversation service for initial sales and customer support. Depending on the agreed plan and tested integrations, possible modules include lead capture, quotes, orders, opt-in broadcasts, agent commissions, payment integration and bookings. It may reduce repetitive FAQ work, but response times, sales results, capacity and data isolation are not guaranteed. What business tasks would you like to automate?"
                )
            return (
                "Tuan, LeeA ialah pembantu perbualan AI untuk pertanyaan jualan dan sokongan awal melalui WhatsApp. Bergantung pada pakej dan integrasi yang diuji, skop boleh merangkumi prospek, sebut harga, pesanan, broadcast berizin, komisen ejen, bayaran dan tempahan. Ia berpotensi mengurangkan kerja FAQ berulang, tetapi tiada jaminan 80% FAQ selesai, balasan dalam saat pertama, peningkatan jualan, ratusan chat serentak atau data 100% terasing. Urusan apa yang tuan ingin automasikan?"
            )

        if any(term in msg_lower for term in ("skop kerja bot", "skop bot whatsapp", "bot brain deep scope", "bot scope")):
            if "bot scope" in msg_lower:
                return (
                    "Tuan, the proposed bot scope covers lead screening, product FAQs, quotes/orders, bookings, payments, agents, after-sales support and human escalation. CRM storage, reminders, real-time slot locks, payment verification, commissions and quota top-ups require separate integrations and testing. I have not performed these actions; which module should we scope first?"
                )
            return (
                "Tuan, skop cadangan bot merangkumi saringan prospek, FAQ produk, sebut harga/pesanan, tempahan, bayaran, ejen/dropship, selepas jualan dan eskalasi staf. Simpanan CRM, follow-up, kunci slot, pengesahan bayaran, komisen dan top-up memerlukan integrasi serta ujian berasingan; saya belum melaksanakan tindakan tersebut. Modul mana yang tuan mahu tetapkan dahulu?"
            )

        if any(term in msg_lower for term in ("skop yang tidak boleh", "larangan bot", "bot limitations", "prohibited bot tasks")):
            if any(term in msg_lower for term in ("bot limitations", "prohibited bot tasks")):
                return ("Tuan, LeeA must not send unsolicited blasts or prohibited content, register Meta numbers independently, approve credit, exceptional discounts or unverified payments, sign contracts, give high-risk professional advice, expose secrets or sensitive customer data, impersonate a human, change server code or handle unknown files. Crises and major negotiations need human review. These are operating rules, not proof of technical enforcement; please confirm controls with our team.")
            return ("Tuan, LeeA tidak boleh menghantar blast tanpa izin atau kandungan terlarang, mendaftar nombor Meta sendiri, meluluskan kredit/diskaun luar had/bayaran tanpa semakan, menandatangani kontrak, memberi nasihat profesional berisiko, mendedahkan rahsia atau data sensitif, menyamar sebagai manusia, mengubah kod pelayan atau mengendalikan fail asing. Krisis dan rundingan besar perlu semakan manusia. Ini batas panduan, bukan bukti kawalan teknikal telah dikuatkuasakan; sila sahkan dengan pasukan kami.")

        if is_payment:
            if is_english:
                return (
                    f"💬 [Customer Service - Architech Systems ({self.client_id})]: "
                    f"Thank you for the payment update, tuan. Please use the official secure payment verification channel confirmed by our team; do not share sensitive banking details here. "
                    f"Our team or the payment provider must verify the transaction before activation. Do not share passwords or API keys."
                )
            else:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - Architech Systems ({self.client_id})]: "
                    f"Terima kasih atas makluman bayaran, tuan. Sila gunakan saluran rasmi yang selamat setelah disahkan oleh staf; jangan kongsi butiran perbankan sensitif di chat ini. "
                    f"Bayaran dan pengaktifan tertakluk pada semakan staf atau rekod penyedia bayaran. Jangan kongsikan kata laluan atau API key di sini."
                )

        if needs_escalation:
            unique_code = random.randint(1000, 9999)
            ticket_id = f"TICK-{datetime.now().strftime('%y%m%d%H%M%S')}-{unique_code}"
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            sent = self._dispatch_smtp_email(ticket_id, customer_phone, customer_email, customer_message, current_time)

            if is_english:
                return (
                    f"💬 [Customer Service - Architech Systems ({self.client_id})]: "
                    f"I understand, tuan. Please contact support directly if needed.\n\n"
                    f"📌 **Reference (not a confirmed ticket):** `{ticket_id}`\n"
                    f"📅 **Time:** {current_time}\n\n"
                    + ("The support email was sent." if sent else "The support email could not be confirmed; please contact support directly.")
                )
            else:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - Architech Systems ({self.client_id})]: "
                    f"Baik tuan, saya faham. Sila hubungi pasukan sokongan secara terus jika perlu:\n\n"
                    f"📌 **Rujukan (bukan tiket yang disahkan):** `{ticket_id}`\n"
                    f"📅 **Masa:** {current_time}\n\n"
                    + ("E-mel sokongan telah dihantar." if sent else "Penghantaran e-mel sokongan tidak dapat disahkan; sila hubungi sokongan secara terus.")
                )

        if any(term in msg_lower for term in ("renew", "grace period", "suspend", "refund", "upgrade", "pembaharuan", "tempoh bertenang", "gantung", "pulangan", "naik taraf")):
            if is_english or any(term in msg_lower for term in ("renew", "grace period", "suspend", "refund", "upgrade")):
                return (
                    f"💬 [Customer Service - Architech Systems]: Tuan, the reference policy is a one-time setup fee (Basic RM149, Pro RM499, Advance RM999) and RM130/month for main plans. The proposed terms are non-refundable setup fees subject to the written agreement, monthly renewal on the registration date and a 3-day grace period before possible suspension. Upgrade setup-fee differences are Basic→Pro RM350, Pro→Advance RM500, or Basic→Advance RM850. Please confirm your contract, account dates, invoice and any third-party charges with our team; I cannot verify account status or promise automatic suspension, reactivation or zero extra charges."
                )
            return (
                f"💬 [Pegawai Khidmat Pelanggan - Architech Systems]: Tuan, polisi rujukan menetapkan yuran setup sekali (Basic RM149, Pro RM499, Advance RM999) dan RM130/bulan untuk pakej utama. Yuran setup dicadangkan tidak dipulangkan tertakluk pada terma bertulis; pembaharuan ikut tarikh pendaftaran dan tempoh bertenang 3 hari sebelum kemungkinan penggantungan. Beza yuran setup naik taraf: Basic→Pro RM350, Pro→Advance RM500, Basic→Advance RM850. Sila sahkan kontrak, tarikh akaun, invois serta caj pihak ketiga dengan staf; saya tidak dapat mengesahkan status akaun atau menjanjikan penggantungan/pengaktifan automatik mahupun tiada caj tambahan."
            )

        if is_english:
            if "ssm" in msg_lower or "company" in msg_lower or "address" in msg_lower:
                return (
                    f"💬 [Customer Service - Architech Systems]: "
                    f"Architech Systems (SSM: 202603255098 / 003893898-X) is located at Laman Niaga, Jalan AWF5, Ampang Waterfront, 68000 Ampang, Selangor. Visit us at www.architechsystems.my!"
                )
            elif "price" in msg_lower or "package" in msg_lower or "bot" in msg_lower or "sea" in msg_lower:
                if "advance" in msg_lower:
                    return (
                        f"💬 [Customer Service - Architech Systems]: "
                        f"Tuan, Advance is listed at RM999 one-time setup and RM130/month. Proposed scope includes up to 5 WhatsApp lines, AI chat/human takeover, quotes, orders, payment integration, agent commissions, follow-ups, broadcasts, lead capture, alerts and a dashboard. Availability depends on configuration, integrations and Meta approval; payment confirmation, message delivery and data security are not guaranteed. Which modules would you like us to verify?"
                    )
                return (
                    f"💬 [Customer Service - Architech Systems]: "
                    f"Hi tuan! Indicative setup: Basic RM149, Pro RM499, Advance RM999; main plans RM130/month. Advanced features such as payments, broadcast and booking require scope and availability confirmation. Which features do you need?"
                )
            else:
                return (
                    f"💬 [Customer Service - Architech Systems]: "
                    f"Message received, tuan. Would you like details on SEA Bot plans or help with your existing system?"
                )
        else:
            if "ssm" in msg_lower or "syarikat" in msg_lower or "alamat" in msg_lower:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - Architech Systems]: "
                    f"Architech Systems berdaftar rasmi di bawah SSM (No: 202603255098 / 003893898-X) yang beralamat di Laman Niaga, Jalan AWF5, Ampang Waterfront, 68000 Ampang, Selangor. Layari portal rasmi kami di www.architechsystems.my!"
                )
            elif "harga" in msg_lower or "pakej" in msg_lower or "sea bot" in msg_lower or "pelan" in msg_lower:
                if "advance" in msg_lower:
                    return (
                        f"💬 [Pegawai Khidmat Pelanggan - Architech Systems]: "
                        f"Tuan, harga rujukan Advance ialah setup RM999 sekali dan RM130/bulan. Skop cadangan: sehingga 5 talian WhatsApp, AI dan human takeover, sebut harga/pesanan, integrasi bayaran, komisen ejen, follow-up, broadcast, Lead Catcher, amaran admin serta dashboard. Ketersediaan bergantung pada konfigurasi, integrasi dan polisi Meta; pengesahan bayaran, penghantaran mesej dan keselamatan data tidak dijamin secara mutlak. Modul mana yang tuan mahu kami sahkan dahulu?"
                    )
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - Architech Systems]: "
                    f"Hai tuan! Harga rujukan setup: Basic RM149, Pro RM499, Advance RM999; pakej utama RM130/bulan. Ciri seperti bayaran automatik, broadcast dan tempahan pintar tertakluk pengesahan skop dan ketersediaan. Tuan perlukan ciri yang mana?"
                )
            else:
                return (
                    f"💬 [Pegawai Khidmat Pelanggan - Architech Systems]: "
                    f"Baik tuan! Mesej '{customer_message}' telah diterima. Saya boleh bantu tentang pakej SEA Bot, penggunaan sistem atau isu sokongan. Tuan perlukan bantuan yang mana satu?"
                )

    def _dispatch_smtp_email(self, ticket_id: str, phone: str, email: str, message: str, timestamp: str):
        sender_email = os.getenv("SMTP_EMAIL", "")
        sender_password = os.getenv("SMTP_PASSWORD", "")
        recipient_email = os.getenv("SMTP_RECIPIENT_EMAIL", "")

        if not all((sender_email, sender_password, recipient_email)):
            return False

        subject = f"[ALERTS - {self.client_id}] Rujukan Sokongan: {ticket_id}"
        body = (
            f"Rujukan: {ticket_id}\nMasa: {timestamp}\n"
            f"Telefon: {phone}\nE-mel pelanggan: {email}\nMesej: {message}"
        )
        mail = MIMEMultipart()
        mail["From"] = sender_email
        mail["To"] = recipient_email
        mail["Subject"] = subject
        mail.attach(MIMEText(body, "plain", "utf-8"))
        try:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, mail.as_string())
        except (OSError, smtplib.SMTPException):
            return False
        return True