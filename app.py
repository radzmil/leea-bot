import hashlib
import json
import logging
import os
import re
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from leea_engine import LEEASystemEngine
from company_knowledge import load_company_knowledge
from demo_examples import wants_product_image
import requests

# Pastikan import psycopg2 untuk sambungan PostgreSQL
import psycopg2

# Konfigurasi Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

app = Flask(__name__)

ASAI_API_KEY = os.getenv("ASAI_API_KEY", "")
ASAI_MODEL = os.getenv("ASAI_MODEL", "asai/claude-haiku-4.5")
ASAI_BASE_URL = os.getenv("API_BASE_URL", "https://serveras.click/v1").rstrip("/")

# URL Pangkalan Data PostgreSQL (Tarik dari Variables Railway)
DATABASE_URL = os.getenv("DATABASE_URL")

# Kredensial & Konfigurasi ToyyibPay & SMTP E-mel
TOYYIBPAY_SECRET_KEY = os.getenv("TOYYIBPAY_SECRET_KEY", "")
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# URL Web App Google Sheets Baharu (DB_architech_laboratory / Log_Chat)
GOOGLE_SHEET_WEB_APP_URL = os.getenv("GOOGLE_SHEET_WEB_APP_URL", "")
GOOGLE_SHEET_CHAT_HISTORY_URL = os.getenv("GOOGLE_SHEET_CHAT_HISTORY_URL", "")

# Inisialisasi Klien Gemini dan enjin setiap akaun
CLIENT_ENGINES = {
    "architechlaboratory": LEEASystemEngine(client_name="Architech Systems"),
    "aluzlia": LEEASystemEngine(client_name="Aluzlia"),
}

# SIMPANAN DATA MULTI-TENANT
CLIENTS_DATABASE = {
    "architechlaboratory": {
        "username": "architechlaboratory",
        "verify_token": os.getenv("VERIFY_TOKEN_ARCHITECH", ""),
        "whatsapp_token": os.getenv(
            "WHATSAPP_TOKEN", os.getenv("WHATSAPP_TOKEN_ARCHITECH", "")
        ),
        "whatsapp_phone_id": os.getenv(
            "WHATSAPP_PHONE_ID", os.getenv("WHATSAPP_PHONE_ID_ARCHITECH", "")
        ),
        "demo_product_image_url": os.getenv("DEMO_PRODUCT_IMAGE_URL_ARCHITECH", ""),
        "live_chats": [],
    },
    "aluzlia": {
        "username": "aluzlia",
        "verify_token": os.getenv("VERIFY_TOKEN_ALUZLIA", ""),
        "whatsapp_token": os.getenv("WHATSAPP_TOKEN_ALUZLIA", ""),
        "whatsapp_phone_id": os.getenv("WHATSAPP_PHONE_ID_ALUZLIA", ""),
        "demo_product_image_url": os.getenv("DEMO_PRODUCT_IMAGE_URL_ALUZLIA", ""),
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
              "SEA Bot Multi-Tenant Backend with ToyyibPay & Notifications"
          ),
          "company": "Architech Systems",
          "registered_tenants": list(CLIENTS_DATABASE.keys()),
      }),
      200,
  )


# --- FUNGSI SIMPAN KE POSTGRESQL (UNTUK PAPARAN DASHBOARD VERCEL) ---
def save_chat_to_postgres(username, sender_phone, message_text, role="customer"):
    """
    Menyimpan mesej secara langsung ke jadual 'messages' PostgreSQL.
    Jika jadual belum ada, pelayan akan cipta secara automatik.
    """
    if not DATABASE_URL:
        logging.warning("DATABASE_URL tiada. Melangkau proses penyimpanan PostgreSQL.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # 1. Bina jadual 'messages' jika ia belum wujud dalam database
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                client_id INTEGER,
                sender VARCHAR(50),
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Dapatkan ID Klien berdasarkan nama pengguna
        cursor.execute("SELECT id FROM clients WHERE username = %s;", (username,))
        res = cursor.fetchone()

        if res:
            client_id = res[0]

            # Jika mesej daripada pelanggan, rekod sender sbg no telefon. Jika tidak, "Zulfa Bot".
            db_sender = sender_phone if role == "customer" else "Zulfa Bot"

            # 3. Masukkan rekod mesej ke dalam pangkalan data
            cursor.execute(
                "INSERT INTO messages (client_id, sender, message, timestamp) VALUES (%s, %s, %s, NOW());",
                (client_id, db_sender, message_text)
            )

            conn.commit()
            logging.info(f"Mesej daripada {db_sender} berjaya didaftarkan ke PostgreSQL.")
        else:
            logging.warning(f"Sistem gagal mencari ID untuk klien: {username}")

        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Ralat menyambung/menyimpan ke PostgreSQL: {e}")


def load_chat_context(username, sender_phone, limit=10):
  """Ambil perbualan terkini bagi tenant dan nombor ini sahaja."""
  if not DATABASE_URL or not sender_phone:
    return []
  try:
    with psycopg2.connect(DATABASE_URL) as conn:
      with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM clients WHERE username = %s", (username,))
        row = cursor.fetchone()
        if not row:
          return []
        cursor.execute(
            "SELECT sender, message FROM messages WHERE client_id = %s "
            "AND sender IN (%s, %s, %s) ORDER BY id DESC LIMIT %s",
            (row[0], sender_phone, "Zulfa Bot", "SEA Bot", limit),
        )
        return [{"sender": "customer" if sender == sender_phone else "agent",
                 "text": text} for sender, text in reversed(cursor.fetchall())]
  except Exception as exc:
    logging.warning("Sejarah perbualan tidak tersedia: %s", exc)
    return []


# --- FUNGSI HANTAR E-MEL TERIMA KASIH & PENGESAHAN ---
def send_payment_success_email(
    client_email, client_name, client_id, new_expiry_date
):
  """Menghantar e-mel rasmi kejayaan langganan menggunakan architechlaboratory@gmail.com."""
  subject = "Pembayaran Berjaya - Terima Kasih Kerana Melanggan SEA Bot!"

  body = f"""Hi {client_name},

Terima kasih atas pembayaran anda! Transaksi langganan anda untuk SEA Bot WhatsApp Automation telah berjaya diproses dan disahkan.

- ID Klien: {client_id}
- Jumlah Dibayar: RM130.00
- Tarikh Luput Akaun Baharu: {new_expiry_date}

Sistem AI dan bot automasi WhatsApp anda kini terus aktif sepenuhnya tanpa sebarang gangguan. Anda boleh terus log masuk ke portal untuk memantau prestasi kempen dan interaksi live chat.

Jika anda mempunyai sebarang pertanyaan atau memerlukan bantuan teknikal lanjut, hubungi admin Architech Systems di 011-2368-7357.

Yang ikhlas,
Pasukan Pengurusan & Operasi Architech Systems"""

  message = MIMEMultipart()
  message["From"] = SMTP_EMAIL
  message["To"] = client_email
  message["Subject"] = subject
  message.attach(MIMEText(body, "plain"))

  if not SMTP_EMAIL or not SMTP_PASSWORD:
    logging.error("Kredensial SMTP tidak lengkap; e-mel tidak dihantar.")
    return

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
  """Menghantar mesej ucapan terima kasih secara automatik melalui bot WhatsApp SEA Bot."""
  if not client_phone:
    return

  formatted_phone = client_phone.replace("+", "").strip()

  whatsapp_message = (
      f"Hi *{client_name}*! 🌟\n\nTerima kasih kerana melakukan pembayaran"
      " langganan bulanan *RM130* untuk SEA Bot WhatsApp Automation.\n\n📅"
      f" *Tarikh Luput Akaun Baharu:* {new_expiry_date}\n\nBot dan sistem AI"
      " anda kini terus aktif sepenuhnya tanpa sebarang gangguan. Sekiranya ada"
       " sebarang persoalan, hubungi admin Architech Systems"
       " di 011-2368-7357.\n\nTerima kasih kerana menyokong"
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

    if TOYYIBPAY_SECRET_KEY and received_hash == expected_hash:
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
@app.route("/webhook/", methods=["GET"])
def verify_webhook(username="architechlaboratory"):
  client_data = CLIENTS_DATABASE.get(username)
  if client_data is None:
    return "Unknown tenant", 404

  mode = request.args.get("hub.mode")
  token = request.args.get("hub.verify_token")
  challenge = request.args.get("hub.challenge")

  if mode and token:
    if mode == "subscribe" and client_data["verify_token"] and token == client_data["verify_token"]:
      logging.info(f"WEBHOOK_VERIFIED untuk Akaun: {username}")
      return challenge, 200
    else:
      return "Forbidden Token", 403
  return "Bad Request", 400


@app.route("/webhook", methods=["POST"])
@app.route("/webhook/", methods=["POST"])
def handle_webhook(username="architechlaboratory"):
  client_data = CLIENTS_DATABASE.get(username)
  if client_data is None:
    return "Unknown tenant", 404

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

              chats = client_data["live_chats"]
              existing_chat = next((c for c in chats if c["phone"].lstrip("+") == sender_phone.lstrip("+")), None)
              context = (existing_chat["messages"][-10:] if existing_chat else
                         load_chat_context(username, sender_phone))
              save_customer_to_google_sheets(username, sender_phone)
              save_chat_history_to_sheets(
                  username,
                  sender_phone,
                  sender="Pelanggan",
                  message_text=message_body,
                  role="customer",
              )

              # SIMPAN MESEJ MASUK KE POSTGRESQL DASHBOARD
              save_chat_to_postgres(username, sender_phone, message_body, role="customer")

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
                  "time": datetime.now().strftime("%I:%M %p"),
              })
              chat_item["lastMessage"] = message_body

              if chat_item["mode"] == "ai":
                response_text = generate_ai_response(message_body, username, sender_phone, context)
                if wants_product_image(message_body):
                  image_url = client_data.get("demo_product_image_url", "")
                  if image_url.startswith("https://"):
                    if send_whatsapp_image(
                        client_data["whatsapp_phone_id"],
                        client_data["whatsapp_token"], sender_phone, image_url
                    ):
                      response_text = "Tuan, ini gambar produk demo. Ini hanya contoh; gambar dan maklumat produk sebenar perlu disahkan dengan staf."
                    else:
                      response_text = "Maaf tuan, gambar demo belum berjaya dihantar. Sila minta staf tunjukkan contoh produk melalui saluran rasmi."
                send_whatsapp_message(
                    client_data["whatsapp_phone_id"],
                    client_data["whatsapp_token"],
                    sender_phone,
                    response_text,
                )
                chat_item["messages"].append({
                    "sender": "agent",
                    "text": response_text,
                    "time": datetime.now().strftime("%I:%M %p"),
                })
                chat_item["lastMessage"] = response_text

                save_chat_history_to_sheets(
                    username,
                    sender_phone,
                    sender="SEA Bot",
                    message_text=response_text,
                    role="agent",
                )

                # SIMPAN BALASAN BOT KE POSTGRESQL DASHBOARD
                save_chat_to_postgres(username, sender_phone, response_text, role="agent")

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
    portal_link = "https://leeasystem.vercel.app"

    activation_message = (
        f"Hai *{company}*! 👋\n\nAkaun SEA Bot anda telah berjaya"
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
@app.route("/api//chats", methods=["GET", "OPTIONS"])
def get_live_chats(username="architechlaboratory"):
  if request.method == "OPTIONS":
    return jsonify({"success": True}), 200

  client_data = CLIENTS_DATABASE.get(username)
  if client_data is None:
    return jsonify({"success": False, "error": "Unknown tenant"}), 404
  return (
      jsonify({
          "success": True,
          "username": username,
          "chats": client_data["live_chats"],
      }),
      200,
  )


@app.route("/api/chats/reply", methods=["POST", "OPTIONS"])
@app.route("/api//chats/reply", methods=["POST", "OPTIONS"])
def reply_live_chat(username="architechlaboratory"):
  if request.method == "OPTIONS":
    return jsonify({"success": True}), 200

  client_data = CLIENTS_DATABASE.get(username)
  if client_data is None:
    return jsonify({"success": False, "error": "Unknown tenant"}), 404
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
    if chat["id"] == chat_id or chat["phone"] == phone:
      chat["messages"].append(
          {"sender": "agent", "text": text, "time": datetime.now().strftime("%I:%M %p")}
      )
      chat["lastMessage"] = text
      save_chat_history_to_sheets(
          username, phone, sender="Agent", message_text=text, role="agent"
      )

  return jsonify({"success": True}), 200


@app.route("/api/chats/toggle-mode", methods=["POST", "OPTIONS"])
@app.route("/api//chats/toggle-mode", methods=["POST", "OPTIONS"])
def toggle_chat_mode(username="architechlaboratory"):
  if request.method == "OPTIONS":
    return jsonify({"success": True}), 200

  client_data = CLIENTS_DATABASE.get(username)
  if client_data is None:
    return jsonify({"success": False, "error": "Unknown tenant"}), 404
  data = request.get_json()
  chat_id = data.get("chat_id")
  phone = data.get("phone")

  for chat in client_data["live_chats"]:
    if (chat_id and chat["id"] == chat_id) or (phone and chat["phone"] == phone):
      chat["mode"] = "human" if chat["mode"] == "ai" else "ai"

  return jsonify({"success": True}), 200


def generate_ai_response(prompt_text, username="architechlaboratory", sender_phone="", history=None):
  engine = CLIENT_ENGINES.get(username)
  if engine is None:
    raise ValueError(f"Unknown tenant: {username}")
  # Jawab terus soalan ringkas ini; jangan biarkan pangkalan pengetahuan panjang
  # bertukar menjadi senarai jualan yang tidak diminta.
  normalized = re.sub(r"[^\w\s]", " ", prompt_text.lower())
  if (username == "architechlaboratory"
      and len(normalized.split()) <= 15
      and re.search(r"\b(selain|ade|ada)\b", normalized)
      and re.search(r"\b(sistem|servis|service|buat|produk)\b", normalized)
      and re.search(r"\b(apa|ape|lagi|lain)\b", normalized)):
    return ("Ada. Selain bot WhatsApp LeeA, Architech Systems juga buat "
            "sistem automasi dan perisian ikut keperluan bisnes.")
  engine.tenant_username = username
  def respond(message, brain):
    return _generate_asai_response(message, brain, history, username)
  return engine.process_incoming_whatsapp_message(sender_phone, prompt_text, responder=respond)


def _generate_asai_response(prompt_text, brain, history=None, username="architechlaboratory"):
  try:
    if not ASAI_API_KEY:
      raise ValueError("ASAI_API_KEY belum dikonfigurasi")
    instruction = (brain.persona_instruction +
                   "\nFAKTA SYARIKAT DISAHKAN (rujuk hanya jika relevan, jangan salin semuanya):\n" +
                   load_company_knowledge(username))
    messages = [{"role": "system", "content": instruction}]
    messages += [{"role": "user" if item["sender"] == "customer" else "assistant",
                  "content": item["text"][:1000]}
                 for item in (history or [])[-10:]
                 if item.get("sender") in ("customer", "agent") and item.get("text")]
    messages.append({"role": "user", "content": prompt_text})
    response = requests.post(
        f"{ASAI_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {ASAI_API_KEY}", "Content-Type": "application/json"},
        json={"model": ASAI_MODEL, "messages": messages, "max_tokens": 350},
        timeout=30,
    )
    response.raise_for_status()
    answer = response.json()["choices"][0]["message"]["content"]
    if not isinstance(answer, str) or not answer.strip():
      raise ValueError("Jawapan AI kosong")
    return answer.strip()
  except Exception as e:
    logging.error("Ralat asAI API: %s", type(e).__name__)
    try:
      return brain.generate_response(prompt_text)
    except Exception as e2:
      logging.error(f"Ralat Fallback: {e2}")
      return (
          "Maaf tuan, sistem sedang mengalami gangguan sementara. Sila cuba"
          " mesej semula sebentar lagi."
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


def send_whatsapp_image(phone_id, token, to_number, image_url):
  """Hantar imej demo daripada URL HTTPS yang boleh diakses oleh Meta."""
  if not phone_id or not token or not image_url.startswith("https://"):
    return False
  try:
    response = requests.post(
        f"https://graph.facebook.com/v21.0/{phone_id}/messages",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"messaging_product": "whatsapp", "to": to_number, "type": "image",
              "image": {"link": image_url}},
        timeout=15,
    )
    if not response.ok:
      logging.error("Penghantaran imej demo gagal: HTTP %s", response.status_code)
      return False
    return True
  except requests.RequestException as error:
    logging.error("Ralat menghantar imej demo: %s", error)
    return False


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)