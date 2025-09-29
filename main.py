import os
import requests
from flask import Flask, request
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print("Groq client initialization error:", e)
else:
    print("GROQ_API_KEY missing; replies will fall back to echo.")

# validate the webhook
@app.route("/webhook", methods=["GET"])#type: ignore
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
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
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
    """Create a reply using Groq API if configured; otherwise return a simple echo."""
    default_reply = f"Echo: {user_text}"
    if not client:
        return default_reply

    try:
        chat_completion = client.chat.completions.create(
            # we will use this model because its the only one i found that is is not decommissioned and free 
            model="openai/gpt-oss-20B",
            messages=[
                {"role": "system", "content": "You are a concise, helpful assistant for WhatsApp. Be friendly and answer clearly."},
                {"role": "user", "content": user_text},
            ],
        )
        ai_text = chat_completion.choices[0].message.content.strip()# type: ignore
        return ai_text or default_reply
    except Exception as e:
        print("Groq error:", e)
        return "Sorry, I couldn't process that. Please try again."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
