import os
import requests
from flask import Flask, request
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
      
        print("Gemini configure error:", e)
else:
    print("GOOGLE_API_KEY missing; replies will fall back to echo.")
# validate the webhook
@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "Invalid verification token", 403

# handle incoming messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print("Incoming:", data)

    try:
       
        for entry in (data.get("entry") or []):
            for change in (entry.get("changes") or []):
                value = change.get("value", {})

              
                messages = value.get("messages") or []
                if messages:
                    message = messages[0]
                    sender = message.get("from")
                  
                    text = (message.get("text") or {}).get("body")
                    if text:
                        print(f"User {sender} said: {text}")
                      
                        ai_reply = generate_ai_reply(text)
                        send_message(sender, ai_reply)
                    else:
                        print(f"Incoming message from {sender} without text payload. Skipping reply.")

               
                statuses = value.get("statuses") or []
                if statuses:
                    status = statuses[0]
                    msg_id = status.get("id")
                    recipient_id = status.get("recipient_id")
                    st = status.get("status")
                    print(f"Message {msg_id} to {recipient_id} is now {st}")

    except Exception as e:
        print("❌ Error processing webhook:", e)

    return "EVENT_RECEIVED", 200


def send_message(to, message):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    r = requests.post(url, headers=headers, json=payload)
    print("Reply status:", r.status_code, r.text)
    return r.json()


def generate_ai_reply(user_text: str) -> str:
    """Create a reply using Google Gemini if configured; otherwise return a simple echo.

    Keeps a  helpful style suitable for WhatsApp. Includes basic error handling
    so the webhook never crashes even if Gemini is unavailable.
    """
    default_reply = f"Echo: {user_text}"
    if not GOOGLE_API_KEY:
        return default_reply

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            "You are a concise, helpful assistant for WhatsApp. "
            "be friendly, and answer clearly.\n\nUser: " + user_text
        )
        resp = model.generate_content(prompt)
        ai_text = (getattr(resp, "text", None) or "").strip()
        return ai_text or default_reply
    except Exception as e:
        print("Gemini error:", e)
        return "Sorry, I couldn't process that. Please try again."

if __name__ == "__main__":
    app.run(port=5000, debug=True)
# import secrets
# print(secrets.token_hex(16))


