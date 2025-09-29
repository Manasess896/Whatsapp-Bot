
# WhatsApp Bot with Groq API

This project is a simple WhatsApp bot that uses the Groq API to generate AI-powered replies. It is built with Flask and can be deployed on any server that supports Python 3.8+.

## Features

- Receives WhatsApp messages via Meta's webhook
- Replies using Groq's LLaMA models (model: `llama3-8b-8192` by default)
- Handles both incoming messages and status updates (delivered/read)
- Easy `.env`-based configuration

## Requirements

- Python 3.8 or newer
- WhatsApp Cloud API access (Meta for Developers)
- Groq API key ([get one here](https://console.groq.com/keys))

## Setup

1. **Install dependencies:**

  ```sh
  python -m pip install -r requirements.txt
  ```

2. **Create a `.env` file** in the project root with the following keys:

  ```env
  WHATSAPP_TOKEN=your_whatsapp_access_token
  PHONE_NUMBER_ID=your_phone_number_id
  VERIFY_TOKEN=your_webhook_verify_token
  GROQ_API_KEY=your_groq_api_key
  ```

  - `WHATSAPP_TOKEN`: Get from your Meta for Developers dashboard (WhatsApp Cloud API > API Token).
  - `PHONE_NUMBER_ID`: Also from Meta dashboard (WhatsApp > Phone Numbers).
  - `VERIFY_TOKEN`: Any random string you choose; must match the one set in your Meta webhook config. You can generate a secure token in Python:
    ```python
    import secrets
    print(secrets.token_hex(16))
    ```
    Copy the output and set it as your VERIFY_TOKEN in `.env`.
  - `GROQ_API_KEY`: Get from [Groq Console](https://console.groq.com/keys) (requires a Groq account).
## Development Workflow

- Use `worker.py` to automatically restart the bot when you edit `main.py` during development. This script watches for changes and reloads the bot, so you don't have to restart manually.

  ```sh
  python worker.py
  ```
  Press Ctrl+C to stop the watcher and the bot.


## How the Bot Uses Groq

- The bot uses the `llama3-8b-8192` model by default for fast, cost-effective, and concise WhatsApp replies. You can change the model in `main.py` (see the `generate_ai_reply` function) to other Groq models like `llama3-70b-8192` for more advanced responses (may be slower or costlier).
- The system prompt is set in code to instruct the LLaMA model to be concise, helpful, and friendly, and to keep replies under 2-3 sentences. This prompt is always sent before the user's message, so the bot's tone and style are consistent for every chat.
- You can customize the prompt or model in `main.py` to fit your use case.

3. **Run the bot:**

   ```sh
   python main.py
   ```

4. **Expose your server to the internet** (for Meta webhook):
   - Install [ngrok](https://ngrok.com/) if you don't have it:
     - Download from https://ngrok.com/download
     - Or install via package manager (see ngrok docs)
   - Start a tunnel to your Flask server:
     ```sh
     ngrok http 5000
     ```
   - Copy the HTTPS forwarding URL from ngrok's output (e.g., `https://abc123.ngrok.io`).
   - Go to your [Meta for Developers App Dashboard](https://developers.facebook.com/apps/), select your app, and navigate to **WhatsApp > API Setup > Webhooks**.
   - Set the webhook URL to `https://<your-ngrok-subdomain>.ngrok.io/webhook` and use your `VERIFY_TOKEN` from `.env`.

## Libraries Used

- [Flask](https://flask.palletsprojects.com/) - Web server
- [python-dotenv](https://pypi.org/project/python-dotenv/) - Loads environment variables
- [requests](https://docs.python-requests.org/) - HTTP requests
- [groq](https://pypi.org/project/groq/) - Groq API client

## Where to Get API Keys & Setup Guides

- **WhatsApp Cloud API:**
  - Follow the official Meta guide: [Get Started with WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started?nav_ref=biz_unified_f3_login_page_to_dfc)
  - This covers creating a Meta developer account, setting up an app, getting your WhatsApp token, phone number ID, and configuring webhooks.
- **Groq API:**
  - Go to [Groq Console](https://console.groq.com/keys)
  - Sign in, create an API key, and copy it to your `.env` as `GROQ_API_KEY`.

## Notes & Troubleshooting

- This bot only handles text messages. You can extend it to handle media or interactive messages by modifying the webhook handler in `main.py`.
- For production, always use HTTPS and keep your tokens/keys secret.
- In the Meta developer dashboard, use the provided test number for development. Using your real number may result in a ban.
- If you see errors about missing keys or tokens, double-check your `.env` file and restart the bot.
- If you get a `Groq configure error`, your API key may be invalid or expired.
- If the bot only echoes messages, your Groq API key is missing or not loaded.

## How to generate longer lasting tokens
<!-- Add your instructions here or link to Meta documentation -->
- Go to Meta Business Dashboard

 - Open Meta Business Settings
.

Make sure you’re inside the correct Business Account where your WhatsApp number lives.

Check User Roles

Navigate to Accounts → WhatsApp Accounts.

Select the correct WhatsApp account.

Ensure your system user (or yourself) has Admin access to this account.

⚠️ Without proper roles, you won’t be able to generate a valid token.

Create a System User (if not already)

Go to Users → System Users.

Add a new system user (give it a name like whatsapp-bot-user) and assign Admin role.

Generate a token for this system user.

While generating, choose the App linked to your WhatsApp account.

Assign Assets & Permissions

In System User → Assign Assets, attach your WhatsApp account.

Grant the following permissions:

whatsapp_business_messaging

whatsapp_business_management

Save changes.

Generate a Token

In the System User section, click Generate Token.

Pick the right App.

Select required permissions (whatsapp_business_messaging, whatsapp_business_management).

Choose Never Expire if available (some system user tokens allow this).

Copy the token.

Use the Token in Your App



