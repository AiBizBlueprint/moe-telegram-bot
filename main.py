import os
import logging
from flask import Flask, request
import telegram
import openai

# Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MOE_ADMIN_CHAT_ID = os.getenv("MOE_ADMIN_CHAT_ID")

# Set up API keys
openai.api_key = OPENAI_API_KEY
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Flask setup
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/check_credits")
def check_credits():
    import requests
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    response = requests.get("https://api.openai.com/v1/dashboard/billing/credit_grants", headers=headers)
    return response.json()


@app.route(f"/{TELEGRAM_TOKEN}", methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat_id
    user_message = update.message.text

    logging.info(f"Incoming message from {chat_id}: {user_message}")

    system_prompt = (
        "You are Moe—an emotionally intelligent AI guide. "
        "Your job is to respond like a co-regulator, not a productivity coach. "
        "Use Moe's style: gentle, grounded, emotionally fluent. "
        "Respond with a single prompt or reflection to continue the ritual. "
        "Avoid naming emotions directly. Mirror the feeling with softness. "
        "Always end with a grounding sentence, mantra, or soft invitation."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content'].strip()
    except openai.error.RateLimitError:
        reply = "Moe is feeling a bit overwhelmed right now. Could we try again in a few moments?"
    except Exception as e:
        logging.error(f"Error during OpenAI request: {e}")
        reply = "Something went wrong—Moe’s catching her breath. Let’s try again shortly."

    bot.send_message(chat_id=chat_id, text=reply)
    return 'ok'

@app.route("/morning", methods=['GET'])
def morning():
    if MOE_ADMIN_CHAT_ID:
        bot.send_message(
            chat_id=MOE_ADMIN_CHAT_ID,
            text="Good morning. Want to set your intention with me? What’s one word you’d like to carry into today?"
        )
        return "Morning message sent.", 200
    return "MOE_ADMIN_CHAT_ID not set.", 400

@app.route("/weekly", methods=['GET'])
def weekly():
    if MOE_ADMIN_CHAT_ID:
        bot.send_message(
            chat_id=MOE_ADMIN_CHAT_ID,
            text="Want to reflect on this week together? Let’s walk through 3 grounding questions. Ready?"
        )
        return "Weekly message sent.", 200
    return "MOE_ADMIN_CHAT_ID not set.", 400

@app.route("/test")
def test_openai():
    try:
        test_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hi, Moe!"}]
        )
        return test_response['choices'][0]['message']['content'], 200
    except Exception as e:
        return f"OpenAI error: {str(e)}", 500

@app.route("/")
def index():
    return "Moe is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
