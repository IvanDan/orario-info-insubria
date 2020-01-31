# -*- coding: utf-8 -*-
# tabspace set on 4 converted in spaces

import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# Enable logging
from webscraping import aule, timeline2

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
lista_comandi = ('Comandi disponibili:\n'
                 '/orari - invia gli orari\n'
                 '/aule - mostra le aule libere\n'
                 '/timeline - invia le timeline\n'
                 '/timeline2 - mostra la timeline come testo\n'
                 '/inviti - invia gli inviti ai principali gruppi\n'
                 '/help - mostra i comandi disponibili\ntest')


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        'Questo bot ti permette di conoscere gli orari del corso di informatica.\n'+lista_comandi)


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text(lista_comandi)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def orari(bot, update):
    update.message.reply_text('Quale anno?', reply_markup=get_orari_keyboard())


def get_orari_keyboard():
    keyboard = [
        [InlineKeyboardButton(text='Primo anno', callback_data='primo')],
        [InlineKeyboardButton(text='Secondo anno', callback_data='secondo')],
        [InlineKeyboardButton(text='Terzo anno', callback_data='terzo')]
    ]
    return InlineKeyboardMarkup(keyboard)


def timeline(bot, update):
    update.message.reply_text(
        'Quale padiglione?', reply_markup=get_timeline_keyboard())


def get_timeline_keyboard():
    keyboard = [
        [InlineKeyboardButton(text='Monte Generoso', callback_data='Monte')],
        [InlineKeyboardButton(text='Morselli', callback_data='Morselli')],
        [InlineKeyboardButton(text='Seppilli', callback_data='Seppilli')]
    ]
    return InlineKeyboardMarkup(keyboard)


def inviti(bot, update):
    update.message.reply_text(
        'Quale gruppo?', reply_markup=get_inviti_keyboard())


def get_inviti_keyboard():
    keyboard = [
        [InlineKeyboardButton(
            text='Informatica Insubria 2017/2018', callback_data='16/17')],
        [InlineKeyboardButton(
            text='Informatica Insubria (1°/2° anno)', callback_data='17/18')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_orari(bot, to, query, message):
    links = {
        'primo': ('I', '1'),
        'secondo': ('II', '2'),
        'terzo': ('III', '3')
    }

    url = "https://unins.prod.up.cineca.it/calendarioPubblico/contesto=DIPARTIMENTO%2520DI%2520SCIENZE%2520TEORICHE%2520E%2520APPLICATE&titolo=F004%2520INFO%2520{}%2520ANNO%2520I%2520SEMESTRE%252017%252F09%252F2018-21%252F12%252F2018&corsi=F004&anniCorso={}&mostraImpegniAnnullati=true&giorniNonVisualizzati=0&coloraPer=docente&lang=it".format(
        *links[query.data])
    bot.edit_message_text(chat_id=query.message.chat.id, message_id=message,
                          text='<a href="{}">'
                               'Link orari {}</a>'.format(url, query.data), parse_mode='HTML')
    bot.answer_callback_query(callback_query_id=query.id)


def get_timeline(bot, to, query, message):
    links = {
        'Monte': 'mtg',
        'Seppilli': 'sep',
        'Morselli': 'mrs'
    }

    url = "http://timeline.uninsubria.it/index.php?cid=&m=&view=pc&sede={}".format(
        links[query.data])
    bot.edit_message_text(chat_id=query.message.chat.id, message_id=message,
                          text='<a href="{}">Link timeline {}</a>'.format(
                              url, query.data),
                          parse_mode='HTML')
    bot.answer_callback_query(callback_query_id=query.id)


def get_inviti(bot, to, query, message):
    links = {
        '17/18': 'CRFPuw3ZJDAarVZOxuUclw',
        '16/17': 'BVhVgEAjtBn3ER-2fmeEFQ'
    }

    url = "https://t.me/joinchat/{}".format(links[query.data])
    bot.edit_message_text(chat_id=query.message.chat.id, message_id=message,
                          text='<a href="{}">Link gruppo anno {}</a>'.format(
                              url, query.data),
                          parse_mode='HTML')


def callback(bot, update):
    query = update.callback_query

    command = query.data.split()[0][1:]
    params = query.data.split()[1:]

    if command == 'aule':
        aule(bot, update, params)
    elif command == 'timeline2':
        timeline2(bot, update, params)
    else:
        if query.data in ('Monte', 'Morselli', 'Seppilli'):
            get_timeline(bot, query.from_user.id, query,
                         query.message.message_id)
        elif query.data in ('primo', 'secondo', 'terzo'):
            get_orari(bot, query.from_user.id, query, query.message.message_id)
        elif query.data in ('16/17', '17/18'):
            get_inviti(bot, query.from_user.id, query,
                       query.message.message_id)


def main():
    """Start the bot."""
    # TOKEN catch from the command-line
    # TOKEN = sys.argv[1]
    # TOKEN catch from locale var, usable on heroku
    TOKEN = os.environ["TOKEN"]

    # TOKEN = '343204077:AAGk5-IjYTzHzyqaK3iSoKXNyu6j71E3DgM'
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("orari", orari))
    dp.add_handler(CommandHandler("timeline", timeline))
    dp.add_handler(CommandHandler("inviti", inviti))
    dp.add_handler(CommandHandler("aule", aule))
    dp.add_handler(CommandHandler("timeline2", timeline2))
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
