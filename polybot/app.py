import flask

from flask import request
import os
from bot import Bot, QuoteBot, ImageProcessingBot

app = flask.Flask(__name__)

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_APP_URL = os.environ['TELEGRAM_APP_URL']

@app.route('/{}'.format(TELEGRAM_TOKEN), methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    text = update.message.text

    if text.lower() == "hi":
        bot.sendMessage(chat_id=chat_id, text="Hello! How can I assist you today?")

    return 'ok'

@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    bot = ImageProcessingBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)
    # bot = QuoteBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)
    context = ('/home/ubuntu/PolybotServicePythonFursa/polybot/bot_cert.pem', '/home/ubuntu/PolybotServicePythonFursa/polybot/bot_key.pem')
    app.run(host='0.0.0.0', port=8443,ssl_context=context)
