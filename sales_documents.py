"""Draf sebut harga dan invois SEA Bot berdasarkan jadual harga setempat."""

import re
from decimal import Decimal

from leea_engine_packages import get_packages


def get_sales_document(message, tenant):
    text = message.strip()
    lower = text.lower()
    if not re.search(r"\b(sebut harga|quotation|quote|invois|invoice)\b", lower):
        return None
    if tenant != "architechlaboratory":
        return "Maaf, katalog harga akaun ini belum dikonfigurasi. Sila hubungi staf untuk sebut harga atau invois."

    invoice = bool(re.search(r"\b(invois|invoice)\b", lower))
    label = "invois" if invoice else "sebut harga"
    match = re.search(r"(?:\b(?:untuk|atas nama|nama)\s*[:=]?\s*)([^\n,;]+)", text, re.I)
    name = match.group(1).strip() if match else ""
    # Jangan terima mesej bebas sebagai identiti pelanggan atau maklumat bil.
    if not name or len(name) > 80 or re.search(r"\b(invois|invoice|sebut harga|quotation|quote)\b", name, re.I):
        return f"Untuk draf {label} SEA Bot, sila nyatakan nama pelanggan dan pelan. Contoh: '{label} Basic Plan untuk Ali'."

    plan_names = {"basic plan": "Basic Plan", "pro-plan": "Pro-Plan", "pro plan": "Pro-Plan", "advance-plan": "Advance-Plan", "advance plan": "Advance-Plan"}
    found = {plan for key, plan in plan_names.items() if key in lower}
    if len(found) != 1:
        return "Sila pilih tepat satu pelan: Basic Plan, Pro-Plan atau Advance-Plan. Pelan Custom perlu harga disahkan staf."
    plan = found.pop()
    prices = get_packages()[plan]
    setup = Decimal(str(prices["setup_fee_one_off"]))
    monthly = Decimal(str(prices["monthly_fee"]))
    title = "INVOIS DRAF" if invoice else "SEBUT HARGA DRAF"
    return (
        f"{title} — BUKAN DOKUMEN RASMI\n"
        "Architech Systems | SSM 202603255098 (003893898-X)\n"
        "Admin: 011-2368-7357\n"
        f"Pelanggan: {name}\nPelan: SEA Bot {plan}\n"
        f"Yuran setup sekali: RM{setup:.2f}\n"
        f"Langganan bulan pertama: RM{monthly:.2f}\n"
        f"Anggaran jumlah awal: RM{setup + monthly:.2f}\n"
        f"Langganan bulan berikutnya: RM{monthly:.2f}/bulan\n\n"
        "Tertakluk kepada semakan skop, cukai jika berkenaan dan pengesahan staf. "
        "Tiada pesanan atau pembayaran direkod melalui draf ini. "
        "Minta staf keluarkan dokumen rasmi dengan nombor rujukan dan butiran bil yang disahkan. "
        "Untuk urusan pembayaran, hubungi admin 011-2368-7357; akaun bayaran online sedang dikemas kini."
    )