"""Contoh statik yang selamat untuk dipaparkan sebagai teks dalam chat."""

from pathlib import Path
from typing import Optional


DEMO_DIR = Path(__file__).resolve().parent / "demo_examples"


def get_demo_response(message: str) -> Optional[str]:
    text = message.lower()
    if not any(word in text for word in ("contoh", "demo", "sample", "example")):
        return None

    if any(word in text for word in ("sebut harga", "quotation", "quote")):
        return "Tuan, ini contoh sebut harga dalam teks (bukan dokumen rasmi):\n\n" + (DEMO_DIR / "sebut_harga.txt").read_text(encoding="utf-8")
    if any(word in text for word in ("invois", "invoice")):
        return "Tuan, ini contoh invois dalam teks (bukan tuntutan bayaran):\n\n" + (DEMO_DIR / "invois.txt").read_text(encoding="utf-8")
    if any(word in text for word in ("gambar", "image", "photo", "foto", "produk", "product")):
        return (
            "Tuan, gambar produk demo belum tersedia untuk dihantar di akaun ini. "
            "Sila minta staf sediakan imej produk berizin dan pautan HTTPS yang boleh diakses sebelum demo media diaktifkan."
        )
    return None


def wants_product_image(message: str) -> bool:
    text = message.lower()
    return any(word in text for word in ("contoh", "demo", "sample", "example")) and any(
        word in text for word in ("gambar", "image", "photo", "foto", "produk", "product")
    ) and not any(word in text for word in ("sebut harga", "quotation", "quote", "invois", "invoice"))