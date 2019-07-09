# -*- coding: utf-8 -*-
# tabspace set on 4 converted in spaces

import logging
from dataclasses import dataclass
from typing import Dict, List

import bs4
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup

from utils import Time, WebScraper, Date, chunks

tries = 1
scraper = None
edifici = {}


@dataclass
class _Lezione:
    start: Time
    end: Time
    facolta: str
    dettagli: str
    corso: str

    def __eq__(self, other):
        return isinstance(other, _Lezione) and self.corso == other.corso

    def __hash__(self):
        return hash(self.corso)


def _get_aula(aula: bs4.element.Tag) -> Dict[str, List[_Lezione]]:
    lezioni = [lezione.find('div') for lezione in
               aula.find_all('td', {'class': "filled"})]  # trovo tutte le aule in cui c'e' una lezione
    nome_aula = lezioni[0].text
    aula = {
        'nome': nome_aula,
        'lezioni': []
    }
    for i in range(1, len(lezioni)):
        params = lezioni[i].find_all('div')
        ora = params[1].text.split(" - ")
        facolta = params[2].text
        dettagli = params[3].text
        corso = params[4].text if len(params) > 4 else ""

        lezione = _Lezione(Time.from_string(ora[0]), Time.from_string(ora[1]), facolta, dettagli, corso)
        aula['lezioni'].append(lezione)

    return aula


def get_timeline(edificio) -> bool:
    global tries
    global scraper

    scraper = scraper or WebScraper.chrome()

    if edificio not in edifici or edifici[edificio]['data'].day != Date.by_now().day:
        logging.info("web scraping per {} con {} secondo/i di attesa".format(edificio, tries))
        url = "http://timeline.uninsubria.it/browse.php?sede={}"

        timeline = scraper.get_page(url.format(edificio), tries)

        aule = []
        aule_edificio = timeline.find_all('tr')
        for i in range(1, len(aule_edificio)):
            aule.append(_get_aula(aule_edificio[i]))

        if len(aule) > 0:
            edifici[edificio] = {
                'data': Date.by_now(),
                'aule': aule  # lista di aule
            }
            tries = 1
        else:
            tries += 1

            return False

    return True


def _reply(bot: Bot, update: Update, text: str, keyboard: InlineKeyboardMarkup = None):
    message = update.message or update.callback_query.message
    chat_id = message.chat.id
    message_id = message.message_id
    bot.send_message(chat_id=chat_id, reply_to_message_id=message_id, text=text, reply_markup=keyboard,
                     parse_mode='HTML')


def _replace(bot: Bot, update: Update, text: str, keyboard: InlineKeyboardMarkup = None):
    message = update.message or update.callback_query.message
    chat_id = message.chat.id
    message_id = message.message_id
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard, parse_mode='HTML')


def aule(bot: Bot, update: Update, params: List[str] = None):
    if not params:
        keyboard = [
            [InlineKeyboardButton(text="Monte generoso", callback_data="/aule mtg")],
            [InlineKeyboardButton(text="Morselli", callback_data="/aule mrs")],
            [InlineKeyboardButton(text="Seppilli", callback_data="/aule sep")]
        ]
        _reply(bot, update, "Scegli l'edificio", InlineKeyboardMarkup(keyboard))
    elif len(params) == 1:
        edificio = params[0]
        now = Time.now()
        keyboard = []
        for ore in chunks(list(range(0, 20 - now.hour)), 3):
            riga = []
            for ora in ore:
                ora = ora + now.hour
                riga.append(InlineKeyboardButton(text="{}".format(str(Time(hour=ora))),
                                                 callback_data="/aule {} {}".format(edificio, ora)))
            keyboard.append(riga)
        keyboard.append([InlineKeyboardButton(text="Adesso", callback_data="/aule {} {}".format(edificio, now))])
        _replace(bot, update, "Per che ora vuoi controllare se ci sono aule libere?", InlineKeyboardMarkup(keyboard))
    else:
        edificio = params[0]
        when = Time.from_string(params[1])
        _replace(bot, update, "Consulto la timeline...")
        if not get_timeline(edificio):
            return _reply(bot, update, "Errore caricamento timeline. Riprova!")
        text = "Aule libere per le {}\n".format(when)
        for aula in edifici[edificio]['aule']:
            free = True
            stato = ""
            if not len(aula['lezioni']):
                stato = "libera"
            for lezione in aula['lezioni']:
                if when >= lezione.start:
                    if not lezione.corso:
                        stato = "aula studio"
                    elif when >= lezione.end:
                        stato = "libera"
                    else:
                        stato = "occupata almeno fino alle {}".format(lezione.end)
                        free = False
                        break
                elif lezione.corso:  # prossima lezione
                    stato = "libera fino alle {}".format(lezione.start)
                    break
                else:
                    stato = "aula studio"
            if free:
                text += "\u2705 {} {}\n".format(aula['nome'], stato)  # aula libera per ora
            else:
                text += "\u274c {} {}\n".format(aula['nome'], stato)
        _replace(bot, update, text)


def timeline2(bot: Bot, update: Update, params: List[str] = None):
    if not params:
        keyboard = [
            [InlineKeyboardButton(text="Monte generoso", callback_data="/timeline2 mtg")],
            [InlineKeyboardButton(text="Morselli", callback_data="/timeline2 mrs")],
            [InlineKeyboardButton(text="Seppilli", callback_data="/timeline2 sep")]
        ]
        _reply(bot, update, "Scegli l'edificio", InlineKeyboardMarkup(keyboard))
    else:
        edificio = params[0]
        _replace(bot, update, "Consulto la timeline...")
        if not get_timeline(edificio):
            return _reply(bot, update, "Errore caricamento timeline. Riprova!")
        if len(params) == 1:
            keyboard = []
            tutte = edifici[edificio]['aule']
            for gruppo in chunks(tutte, 3):
                riga = []
                for aula in gruppo:
                    riga.append(InlineKeyboardButton(text="{}".format(aula['nome']),
                                                     callback_data="/timeline2 {} {}".format(edificio, aula['nome'])))
                keyboard.append(riga)
            keyboard.append(
                [InlineKeyboardButton(text="Tutte le aule", callback_data="/timeline2 {} tutte".format(edificio))])
            _replace(bot, update, "Scegli l'aula", InlineKeyboardMarkup(keyboard))
        else:
            aula_edificio = " ".join(params[1:])
            text = ""
            for aula in edifici[edificio]['aule']:
                if aula['nome'] == aula_edificio or aula_edificio == "tutte":
                    text += "\n<b>{}</b>\n".format(aula['nome'])
                    if len(aula['lezioni']) > 0:
                        text += "\n".join(
                            "{}-{} {}".format(lezione.start, lezione.end, lezione.corso) for lezione
                            in aula['lezioni'])
                        text += "\n"
            if not text:
                text = "Non sono presenti lezioni in {}!".format(aula_edificio)
            _replace(bot, update, text)
