"""Pengendalian mesej WhatsApp untuk enjin SEA Bot."""

from demo_examples import get_demo_response
from sales_documents import get_sales_document
from payment_guidance import get_payment_guidance


def process_incoming_whatsapp_message(engine, sender_phone: str, message_text: str, responder=None) -> str:
    if not engine.is_active:
        return "Sistem tidak aktif."
    if engine.ai_mode:
        demo_response = get_demo_response(message_text)
        if demo_response is not None:
            response = demo_response
        elif (document := get_sales_document(message_text, getattr(engine, "tenant_username", ""))) is not None:
            response = document
        elif (guidance := get_payment_guidance(message_text, getattr(engine, "tenant_username", ""))) is not None:
            response = guidance
        elif responder is not None:
            response = responder(message_text, engine.brain)
        else:
            response = engine.brain.generate_response(message_text)
        engine.used_chat_tokens += 1
        return response
    return "[HUMAN TOUCH] Mod balasan AI dimatikan. Sila tunggu staf membalas melalui saluran sokongan."