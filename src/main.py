import os
from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
import logging

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logging.getLogger(__name__)


# def start(bot, update):
#     response_message = "=^._.^="
#     bot.send_message(
#         chat_id=update.message.chat_id,
#         text=response_message
#     )


# # def http_cats(bot, update, args):
# #     bot.sendPhoto(
# #         chat_id=update.message.chat_id,
# #         photo=BASE_API_URL + args[0]
# #     )

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    update.message.reply_text('Hi!')


def help_command(update, context):
    print(update.effective_user.id)
    update.message.reply_text('Help!')


def echo(update, context):
    update.message.reply_text(update.message.text)


def unknown(bot, update):
    response_message = "Não entendi! Por favor, use um comando (eles começam com '/')."
    bot.send_message(
        chat_id=update.message.chat_id,
        text=response_message
    )


def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("help", help_command))
    updater.dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo))

    updater.start_polling()
    logging.info("=== Bot running! ===")
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    logging.info("=== Bot shutting down! ===")


if __name__ == '__main__':
    print("press CTRL + C to cancel.")
    main()
