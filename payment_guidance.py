"""Arahan bayaran sementara untuk jualan Architech Systems sahaja."""

import re


def get_payment_guidance(message, tenant):
    if tenant != "architechlaboratory":
        return None
    if not re.search(r"\b(bayar|bayaran|pembayaran|payment|pay|paid|dah bayar|resit|receipt|bank|transfer|duitnow|qr|fpx|toyyibpay)\b", message.lower()):
        return None
    return (
        "Untuk pembayaran produk/perkhidmatan Architech Systems, akaun bayaran online syarikat "
        "sedang dikemas kini. Sila hubungi admin di 011-2368-7357 untuk mendapatkan "
        "kaedah dan butiran pembayaran yang disahkan. Jangan buat bayaran ke akaun atau "
        "pautan yang belum disahkan. Jika tuan sudah membayar, hubungi admin untuk "
        "semakan; resit dalam chat bukan pengesahan bayaran atau pengaktifan servis."
    )