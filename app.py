import hashlib
import json
import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from google import genai
from leea_brain import LEEABrain
import requests

# Konfigurasi Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Kredensial & Konfigurasi ToyyibPay & SMTP E-mel
TOYYIBPAY_SECRET_KEY = "nxehrexd-hx6i-x8au-4idl-3gxlqebywmta"
SMTP_EMAIL = "architechlaboratory@gmail.com"
SMTP_PASSWORD = "H@$$ayang8683"

# URL Web App Google Sheets Baharu (DB_architech_laboratory / Log_Chat)
GAS_ENDPOINT_URL = "https://script.google.com/macros/s/AKfycbyqrB75MYg92E8thEiMPMF1ws1irQpQger3nTZryzR_jIBDHspdSHpE3kHtweCGWHT5/exec"
GOOGLE_SHEET_WEB_APP_URL = os.getenv("GOOGLE_SHEET_WEB_APP_URL", GAS_ENDPOINT_URL)
GOOGLE_SHEET_CHAT_HISTORY_URL = os.getenv("GOOGLE_SHEET_CHAT_HISTORY_URL", GAS_ENDPOINT_URL)

# Inisialisasi Klien Gemini rasmi & LEEABrain
client = genai.Client(api_key=GEMINI_API_KEY)
leea_brain_instance = LEEABrain(client_name="Architech Laboratory")

# SIMPANAN DATA MULTI-TENANT
CLIENTS_DATABASE = {
    "architechlaboratory": {
        "username": "architechlaboratory",
        "verify_token": os.getenv(
            "VERIFY_TOKEN_ARCHITECH", "architech_secure_leea_token_2026"
        ),
        "whatsapp_token": os.getenv(
            "WHATSAPP_TOKEN", os.getenv("WHATSAPP_TOKEN_ARCHITECH", "")
        ),
        "whatsapp_phone_id": os.getenv(
            "WHATSAPP_PHONE_ID", os.getenv("WHATSAPP_PHONE_ID_ARCHITECH", "")
        ),
        "live_chats": [],
    },
    "aluzlia": {
        "username": "aluzlia",
        "verify_token": os.getenv(
            "VERIFY_TOKEN_ALUZLIA", "aluzlia_secure_token_2026"
        ),
        "whatsapp_token": os.getenv("WHATSAPP_TOKEN_ALUZLIA", ""),
        "whatsapp_phone_id": os.getenv("WHATSAPP_PHONE_ID_ALUZLIA", ""),
        "live_chats": [],
    },
}


# --- PELINDUNG CORS UNTUK MEMBENARKAN VERCEL MENGAKSES RAILWAY ---
@app.after_request
def add_cors_headers(response):
  response.headers.add("Access-Control-Allow-Origin", "*")
  response.headers.add(
      "Access-Control-Allow-Headers", "Content-Type,Authorization"
  )
  response.headers.add(
      "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
  )
  return response


@app.route("/", methods=["GET"])
def home():
  """Endpoint semakan kesihatan pelayan bot."""
  return (
      jsonify({
          "status": "online",
          "system": (
              "LEEA Bot Multi-Tenant Backend with ToyyibPay & Notifications"
          ),
          "company": "Architech Laboratory",
          "registered_tenants": list(CLIENTS_DATABASE.keys()),
      }),
      200,
  )


# --- FUNGSI HANTAR E-MEL TERIMA KASIH & PENGESAHAN ---
def send_payment_success_email(
    client_email, client_name, client_id, new_expiry_date
):
  """Menghantar e-mel rasmi kejayaan langganan menggunakan architechlaboratory@gmail.com."""
  subject = "Pembayaran Berjaya - Terima Kasih Kerana Melanggan LEEA System!"

  body = f"""Hi {client_name},

Terima kasih atas pembayaran anda! Transaksi langganan anda untuk LEEA WhatsApp Automation Standard telah berjaya diproses dan disahkan.

- ID Klien: {client_id}
- Jumlah Dibayar: RM130.00
- Tarikh Luput Akaun Baharu: {new_expiry_date}

Sistem AI dan bot automasi WhatsApp anda kini terus aktif sepenuhnya tanpa sebarang gangguan. Anda boleh terus log masuk ke portal untuk memantau prestasi kempen dan interaksi live chat.

Jika anda mempunyai sebarang pertanyaan atau memerlukan bantuan teknikal lanjut, hubungi pasukan sokongan kami pada bila-bila masa melalui talian WhatsApp 24/7 di 60183172114 (LEEA).

Yang ikhlas,
Pasukan Pengurusan & Operasi LEEA System"""

  message = MIMEMultipart()
  message["From"] = SMTP_EMAIL
  message["To"] = client_email
  message["Subject"] = subject
  message.attach(MIMEText(body, "plain"))

  try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.sendmail(SMTP_EMAIL, client_email, message.as_string())
    server.quit()
    logging.info(
        f"E-mel pengesahan pembayaran berjaya dihantar kepada {client_email}"
    )
  except Exception as e:
    logging.error(f"Gagal menghantar e-mel: {e}")


# --- FUNGSI HANTAR MESEJ WHATSAPP TERIMA KASIH MELALUI BOT ---
def send_whatsapp_thank_you(client_phone, client_name, new_expiry_date):
  """Menghantar mesej ucapan terima kasih secara automatik melalui bot WhatsApp LEEA."""
  if not client_phone:
    return

  formatted_phone = client_phone.replace("+", "").strip()

  whatsapp_message = (
      f"Hi *{client_name}*! 🌟\n\nTerima kasih kerana melakukan pembayaran"
      " langganan bulanan *RM130* untuk LEEA WhatsApp Automation Standard.\n\n📅"
      f" *Tarikh Luput Akaun Baharu:* {new_expiry_date}\n\nBot dan sistem AI"
      " anda kini terus aktif sepenuhnya tanpa sebarang gangguan. Sekiranya ada"
      " sebarang persoalan, anda boleh terus berhubung dengan talian support"
      " 24/7 kami di 60183172114.\n\nTerima kasih kerana menyokong"
      " perkhidmatan kami! 🚀"
  )

  default_client = CLIENTS_DATABASE.get("architechlaboratory")
  phone_id = default_client["whatsapp_phone_id"]
  token = default_client["whatsapp_token"]

  if phone_id and token:
    send_whatsapp_message(phone_id, token, formatted_phone, whatsapp_message)
  else:
    logging.error(
        "Kredensial WhatsApp utama tidak lengkap untuk hantar mesej WhatsApp"
        " terima kasih."
    )


# --- WEBHOOK / CALLBACK ENDPOINT UNTUK TOYYIBPAY ---
@app.route("/toyyibpay-callback", methods=["POST"])
def toyyibpay_callback():
  """Endpoint untuk menerima pengesahan status pembayaran daripada ToyyibPay secara automatik."""
  try:
    form_data = request.form

    refno = form_data.get("refno")
    status = form_data.get("status")
    order_id = form_data.get("order_id", "")
    received_hash = form_data.get("hash")
    client_email = form_data.get("email", "client@example.com")
    client_name = form_data.get("name", "Pelanggan")
    client_phone = form_data.get("phone", "")

    raw_string = (
        TOYYIBPAY_SECRET_KEY
        + str(status)
        + str(order_id)
        + str(refno)
        + "ok"
    )
    expected_hash = hashlib.md5(raw_string.encode("utf-8")).hexdigest()

    if received_hash == expected_hash:
      if str(status) == "1":
        new_expiry_date = "27/10/2026"

        send_payment_success_email(
            client_email, client_name, order_id or "CLI-1001", new_expiry_date
        )

        if client_phone:
          send_whatsapp_thank_you(client_phone, client_name, new_expiry_date)

        logging.info(
            f"Callback ToyyibPay berjaya diproses untuk Order ID: {order_id}"
        )
        return (
            jsonify({
                "status": "success",
                "message": "Callback processed & notifications sent",
            }),
            200,
        )
      else:
        logging.warning(
            f"Pembayaran ToyyibPay tidak berjaya atau gagal untuk RefNo: {refno}"
        )
        return (
            jsonify({"status": "failed", "message": "Payment not successful"}),
            200,
        )
    else:
      logging.error("Tandatangan Hash ToyyibPay tidak sah!")
      return (
          jsonify({"status": "error", "message": "Invalid Hash Signature"}),
          400,
      )

  except Exception as e:
    logging.error(f"Ralat memproses ToyyibPay callback: {e}")
    return jsonify({"status": "error", "message": str(e)}), 500


# --- FUNGSI SIMPAN NOMBOR PELANGGAN KE GOOGLE SHEETS ---
def save_customer_to_google_sheets(username, phone):
  """Menghantar nombor telefon pelanggan secara automatik ke Google Drive Sheets."""
  if not GOOGLE_SHEET_WEB_APP_URL:
    return

  payload = {
      "timestamp": datetime.now().strftime("%d/%m/%Y, %I:%M:%S %p"),
      "type": "contact",
      "sender": username,
      "phone": phone,
      "role": "customer",
      "message": f"New Contact Registered: {phone}",
  }

  try:
    response = requests.post(GOOGLE_SHEET_WEB_APP_URL, json=payload, timeout=5)
    logging.info(f"Nombor {phone} direkodkan ke Sheets: {response.text}")
  except Exception as e:
    logging.error(f"Gagal hantar nombor ke Sheets: {e}")


# --- FUNGSI SIMPAN CHAT HISTORY KE GOOGLE SHEETS (6 LAJUR TEPAT) ---
def save_chat_history_to_sheets(username, phone, sender, message_text, role="customer"):
  """Menyimpan rekod mesej masuk/keluar ke pangkalan data tab Log_Chat Google Sheets."""
  if not GOOGLE_SHEET_CHAT_HISTORY_URL:
    return

  payload = {
      "timestamp": datetime.now().strftime("%d/%m/%Y, %I:%M:%S %p"),
      "type": "chat",
      "sender": sender,
      "phone": phone,
      "role": role,
      "message": message_text,
  }

  try:
    response = requests.post(
        GOOGLE_SHEET_CHAT_HISTORY_URL, json=payload, timeout=5
    )
    logging.info(
        f"Chat history drpd {phone} ({sender} / {role}) direkodkan ke Log_Chat."
    )
  except Exception as e:
    logging.error(f"Gagal hantar chat history ke Google Sheets: {e}")


# --- WEBHOOK ENDPOINTS (WHATSAPP) ---

@app.route("/webhook", methods=["GET"])
@app.route("/webhook/<username>", methods=["GET"])
def verify_webhook(username="architechlaboratory"):
  client_data = CLIENTS_DATABASE.get(
      username, CLIENTS_DATABASE["architechlaboratory"]
  )

  mode = request.args.get("hub.mode")
  token = request.args.get("hub.verify_token")
  challenge = request.args.get("hub.challenge")

  if mode and token:
    if mode == "subscribe" and token == client_data["verify_token"]:
      logging.info(f"WEBHOOK_VERIFIED untuk Akaun: {username}")
      return challenge, 200
    else:
      return "Forbidden Token", 403
  return "Bad Request", 400


@app.route("/webhook", methods=["POST"])
@app.route("/webhook/<username>", methods=["POST"])
def handle_webhook(username="architechlaboratory"):
  client_data = CLIENTS_DATABASE.get(
      username, CLIENTS_DATABASE["architechlaboratory"]
  )

  body = request.get_json()
  logging.info(f"Menerima payload webhook untuk akaun [{username}]: {body}")

  try:
    if body.get("object") == "whatsapp_business_account":
      for entry in body.get("entry", []):
        for change in entry.get("changes", []):
          value = change.get("value", {})
          messages = value.get("messages", [])

          if messages:
            message = messages[0]

            sender_phone = str(
                message.get("from")
                or value.get("contacts", [{}])[0].get("wa_id", "")
                or message.get("sender", "")
            ).strip()

            message_body = message.get("text", {}).get("body", "")

            if message_body and sender_phone and sender_phone != "None":
              logging.info(
                  f"Mesej masuk [{username}] drpd {sender_phone}: {message_body}"
              )

              save_customer_to_google_sheets(username, sender_phone)
              save_chat_history_to_sheets(
                  username,
                  sender_phone,
                  sender="Pelanggan",
                  message_text=message_body,
                  role="customer",
              )

              clean_sender = sender_phone.replace("+", "")
              chats = client_data["live_chats"]

              chat_item = next(
                  (
                      c
                      for c in chats
                      if c["phone"].replace("+", "") == clean_sender
                  ),
                  None,
              )

              if not chat_item:
                formatted_phone = (
                    f"+{sender_phone}"
                    if not sender_phone.startswith("+")
                    else sender_phone
                )
                chat_item = {
                    "id": f"chat_{len(chats) + 1}",
                    "phone": formatted_phone,
                    "lastMessage": message_body,
                    "time": "Just now",
                    "mode": "ai",
                    "messages": [],
                }
                chats.insert(0, chat_item)

              chat_item["messages"].append({
                  "sender": "customer",
                  "text": message_body,
                  "time": "Just now",
              })
              chat_item["lastMessage"] = message_body

              if chat_item["mode"] == "ai":
                response_text = generate_ai_response(message_body)
                send_whatsapp_message(
                    client_data["whatsapp_phone_id"],
                    client_data["whatsapp_token"],
                    sender_phone,
                    response_text,
                )
                chat_item["messages"].append({
                    "sender": "agent",
                    "text": response_text,
                    "time": "Just now",
                })
                chat_item["lastMessage"] = response_text

                save_chat_history_to_sheets(
                    username,
                    sender_phone,
                    sender="LEEA Bot",
                    message_text=response_text,
                    role="agent",
                )
              else:
                logging.info(
                    f"Chat {sender_phone} di bawah akaun {username} berada"
                    " dalam mod Human Touch."
                )
            else:
              logging.warning(
                  f"Gagal ekstrak nombor telefon daripada payload: {message}"
              )

      return "EVENT_RECEIVED", 200
    else:
      return "Not Found", 404
  except Exception as e:
    logging.error(f"Ralat memproses webhook akaun {username}: {e}")
    return "Internal Server Error", 500


# --- API PENGAKTIFAN KLIEN & NOTIFIKASI WHATSAPP ---

@app.route("/api/notify-activation", methods=["POST", "OPTIONS"])
def notify_activation():
  if request.method == "OPTIONS":
    return jsonify({"success": True}), 200

  try:
    data = request.get_json() or {}
    client_phone = data.get("phone")
    username = data.get("username")
    company = data.get("company")
    client_email = data.get("email")

    if not client_phone:
      return (
          jsonify({
              "success": False,
              "error": "Nombor telefon klien tidak disertakan.",
          }),
          400,
      )

    formatted_phone = client_phone.replace("+", "").strip()
    portal_link = "https://leea-portal.vercel.app"

    activation_message = (
        f"Hai *{company}*! 👋\n\nAkaun LEEA System anda telah berjaya"
        " didaftarkan dan bot WhatsApp anda kini *RASMI DIAKTIFKAN* 🟢.\n\n🔐"
        " *Maklumat Akses Portal Klien:*\n• Username: *{username}*\n• Pautan"
        f" Portal: {portal_link}\n\n📧 Sila semak peti masuk e-mel anda di"
        f" (*{client_email}*) untuk mendapatkan butiran kata laluan dan"
        " pengesahan rasmi."
    )

    default_client = CLIENTS_DATABASE.get("architechlaboratory")
    phone_id = default_client["whatsapp_phone_id"]
    token = default_client["whatsapp_token"]

    if phone_id and token:
      send_whatsapp_message(phone_id, token, formatted_phone, activation_message)
      return (
          jsonify({
              "success": True,
              "message": (
                  "Notifikasi WhatsApp pengaktifan lengkap berjaya dihantar ke"
                  " klien!"
              ),
          }),
          200,
      )
    else:
      return (
          jsonify({
              "success": False,
              "error": "Kredensial WhatsApp utama pelayan belum lengkap.",
          }),
          500,
      )

  except Exception as e:
    logging.error(f"Ralat menghantar notifikasi pengaktifan: {e}")
    return jsonify({"success": False, "error": str(e)}), 500


# --- API ENDPOINTS EKSKLUSIF UNTUK PORTAL VERCEL ---

@app.route("/api/chats", methods=["GET", "OPTIONS"])
@app.route("/api/<username>/chats", methods=["GET", "OPTIONS"])
def get_live_chats(username="architechlaboratory"):
  if request.method == "OPTIONS":
    return jsonify({"success": True}), 200

  client_data = CLIENTS_DATABASE.get(
      username, CLIENTS_DATABASE["architechlaboratory"]
  )
  return (
      jsonify({
          "success": True,
          "username": username,
          "chats": client_data["live_chats"],
      }),
      200,
  )


@app.route("/api/chats/reply", methods=["POST", "OPTIONS"])
@app.route("/api/<username>/chats/reply", methods=["POST", "OPTIONS"])
def reply_live_chat(username="architechlaboratory"):
  if request.method == "OPTIONS":
    return jsonify({"success": True}), 200

  client_data = CLIENTS_DATABASE.get(
      username, CLIENTS_DATABASE["architechlaboratory"]
  )
  data = request.get_json()
  chat_id = data.get("chat_id")
  phone = data.get("phone")
  text = data.get("text")

  send_whatsapp_message(
      client_data["whatsapp_phone_id"],
      client_data["whatsapp_token"],
      phone.replace("+", ""),
      text,
  )

  for chat in client_data["live_chats"]:
    if chat["id"] == chat_id:
      chat["messages"].append(
          {"sender": "agent", "text": text, "time": "Just now"}
      )
      chat["lastMessage"] = text
      save_chat_history_to_sheets(
          username, phone, sender="Agent", message_text=text, role="agent"
      )

  return jsonify({"success": True}), 200


@app.route("/api/chats/toggle-mode", methods=["POST", "OPTIONS"])
@app.route("/api/<username>/chats/toggle-mode", methods=["POST", "OPTIONS"])
def toggle_chat_mode(username="architechlaboratory"):
  if request.method == "OPTIONS":
    return jsonify({"success": True}), 200

  client_data = CLIENTS_DATABASE.get(
      username, CLIENTS_DATABASE["architechlaboratory"]
  )
  data = request.get_json()
  chat_id = data.get("chat_id")

  for chat in client_data["live_chats"]:
    if chat["id"] == chat_id:
      chat["mode"] = "human" if chat["mode"] == "ai" else "ai"

  return jsonify({"success": True}), 200


def generate_ai_response(prompt_text):
  try:
    persona_instruction = leea_brain_instance.get_leea_persona()
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt_text,
        config={"system_instruction": persona_instruction},
    )
    return response.text
  except Exception as e:
    logging.error(f"Ralat Gemini API: {e}")
    try:
      return leea_brain_instance.generate_response(prompt_text)
    except Exception as e2:
      logging.error(f"Ralat Fallback: {e2}")
      return (
          "Sori bos, line / sistem sedih sikit kejap ni. Cuba try text semula"
          " lepas ni ye."
      )


def send_whatsapp_message(phone_id, token, to_number, message_text):
  if not phone_id or not token:
    logging.error(
        "Kredensial WhatsApp pelanggan tidak lengkap atau kosong."
    )
    return

  url = f"https://graph.facebook.com/v21.0/{phone_id}/messages"
  headers = {
      "Authorization": f"Bearer {token}",
      "Content-Type": "application/json",
  }
  payload = {
      "messaging_product": "whatsapp",
      "to": to_number,
      "type": "text",
      "text": {"body": message_text},
  }

  try:
    response = requests.post(url, headers=headers, json=payload)
    logging.info(
        f"Status hantar WhatsApp: {response.status_code} - {response.text}"
    )
  except Exception as e:
    logging.error(f"Ralat menghantar mesej WhatsApp: {e}")


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)