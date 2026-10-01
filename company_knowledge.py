"""Fakta perniagaan yang diluluskan pemilik; bukan pembelajaran automatik daripada chat."""

import json
import logging
from pathlib import Path


KNOWLEDGE_PATH = Path(__file__).resolve().parent / "company_knowledge.json"


def load_company_knowledge(username):
    try:
        data = json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))
        entry = data.get(username, {})
        if not isinstance(entry, dict):
            return ""
        sections = []
        for key, label in (("company_role", "Peranan syarikat"),
                           ("products", "Produk dan perbezaan")):
            value = entry.get(key)
            if isinstance(value, str) and value.strip():
                sections.append(f"{label}: {value.strip()}")
        return "\n".join(sections)
    except (OSError, ValueError, TypeError) as exc:
        logging.warning("Pengetahuan syarikat tidak tersedia: %s", exc)
        return ""