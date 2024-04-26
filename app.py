from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from main import start, button, message_handler, support_message, help_command

app = Flask(__name__)

# Инициализируйте бота и диспетчера
bot = Bot(token='7039136722:AAGdRluqei0kMd0JPahe-Cx0JS8wCU_XIdc')
dp = Dispatcher(bot, None, workers=10, use_context=True)

# Регистрируйте обработчики
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button))
dp.add_handler(MessageHandler(Filters.text & (~Filters.command), message_handler))
dp.add_handler(MessageHandler(Filters.text & (~Filters.command), support_message))
dp.add_handler(CommandHandler("help", help_command))


@app.route('/', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dp.process_update(update)
    return 'ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443)
