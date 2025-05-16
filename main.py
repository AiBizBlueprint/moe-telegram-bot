import os
import logging
import openai
from flask import Flask, request
import telegram

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MOE_ADMIN_CHAT_ID = os.getenv("MOE_ADMIN_CHAT_ID")

openai.api_key = OPENAI_API_KEY
bot = telegram.Bot(token=TELEGRAM_TOKEN)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route(f"/{TELEGRAM_TOKEN}", methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat_id
    user_message = update.message.text

    # 👇 Add this line to help debug incoming messages
    print(f"Incoming message from {chat_id}: {user_message}")

    prompt = f"""
You are Moe—an emotionally intelligent AI guide...
    """

prompt = "Your job is to respond like a co-regulator, not a productivity coach. Use Moe's style: gentle, grounded, emotionally fluent."
Respond with a single prompt or reflection to continue the ritual.
Avoid naming emotions directly. Mirror the feeling with softness.
Always end with a grounding sentence, mantra, or soft invitation.
"""

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        temperature=0.7,
        n=1,
        stop=None
    )

    reply = response.choices[0].text.strip()
    bot.send_message(chat_id=chat_id, text=reply)
    return 'ok'

@app.route("/morning", methods=['GET'])
def morning():
    if MOE_ADMIN_CHAT_ID:
        bot.send_message(chat_id=MOE_ADMIN_CHAT_ID,
                         text="Good morning. Want to set your intention with me? What’s one word you’d like to carry into today?")
        return "Morning message sent.", 200
    return "MOE_ADMIN_CHAT_ID not set.", 400

@app.route("/weekly", methods=['GET'])
def weekly():
    if MOE_ADMIN_CHAT_ID:
        bot.send_message(chat_id=MOE_ADMIN_CHAT_ID,
                         text="Want to reflect on this week together? Let’s walk through 3 grounding questions. Ready?")
        return "Weekly message sent.", 200
    return "MOE_ADMIN_CHAT_ID not set.", 400

@app.route("/")
def index():
    return "Moe is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
