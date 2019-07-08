#!/usr/bin/env python
# -*- coding: utf-8 -*-
# tabspace set on 2 converted in spaces

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import sys
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
  """Send a message when the command /start is issued."""
  update.message.reply_text('/help - mostra i comandi disponibili')

def help(bot, update):
  """Send a message when the command /help is issued."""
  update.message.reply_text('/help - mostra i comandi disponibili')

def error(bot, update, error):
  """Log Errors caused by Updates."""
  logger.warning('Update "%s" caused error "%s"', update, error)

def callback(bot, update):
  query = update.callback_query

def main():
  """Start the bot."""
  # TOKEN catch from the command-line
  #TOKEN = sys.argv[1]
  # TOKEN catch from locale var, usable on heroku
  TOKEN = os.environ["TOKENTEST"]

  # Create the EventHandler and pass it your bot's token.
  updater = Updater(TOKEN)

  # Get the dispatcher to register handlers
  dp = updater.dispatcher

  # on different commands - answer in Telegram
  dp.add_handler(CommandHandler("start", start))
  dp.add_handler(CommandHandler("help", help))
  dp.add_handler(CallbackQueryHandler(callback))
  
  # log all errors
  dp.add_error_handler(error)

  # Start the Bot
  updater.start_polling()

  # Run the bot until you press Ctrl-C or the process receives SIGINT,
  # SIGTERM or SIGABRT. This should be used most of the time, since
  # start_polling() is non-blocking and will stop the bot gracefully.
  updater.idle()

if __name__ == '__main__':
  main()
