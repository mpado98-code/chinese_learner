# -*- coding: utf-8 -*-
"""
Bot Telegram che ogni mattina invia a Jewel UNA sola espressione cinese da
imparare. L'espressione del giorno puo' essere:
- un'espressione utile (saluti, frasi pratiche, viaggi...),
- una frase romantica in cinese,
- una battuta / modo di dire divertente in cinese.

Tutto e' scritto in alfabeto latino: pinyin con i toni + guida fonetica
all'italiana.

Il primo giorno in assoluto arrivano DUE messaggi:
1) il saluto di Marco a Jewel,
2) l'espressione cinese del giorno (utile / romantica / battuta).

Dai giorni successivi arriva un solo messaggio.
"""

import os
import sys
import time
from datetime import date

import requests

from expressions import EXPRESSIONS
from bonuses import BONUSES

DEFAULT_START_DATE = "2026-06-06"

GREETING = (
    "Ciao Jewel, Marco pensa che tu sia bellissima lo sai? "
    "Ma bando alle ciance, impariamo un po' di cinese."
)

HEADERS = {
    "utile":     "Espressione di oggi",
    "romantica": "Frase romantica di oggi (in cinese)",
    "battuta":   "Espressione divertente di oggi (in cinese)",
}


def days_since_start(start, today):
    return max(0, (today - start).days)


def build_rotation():
    """Costruisce la rotazione giornaliera unica.

    Pattern: 2 utili : 1 bonus. Le bonus alternano romantica/battuta.
    Risultato: ogni giorno UNA sola voce, niente ripetizioni finche' la
    lista non si esaurisce.
    """
    utili = [dict(e, tipo=e.get("tipo", "utile")) for e in EXPRESSIONS]

    # alterno romantiche e battute fra di loro
    romantiche = [dict(b) for b in BONUSES if b.get("tipo") == "romantica"]
    battute    = [dict(b) for b in BONUSES if b.get("tipo") == "battuta"]
    bonus = []
    for i in range(max(len(romantiche), len(battute))):
        if i < len(romantiche):
            bonus.append(romantiche[i])
        if i < len(battute):
            bonus.append(battute[i])

    rotation = []
    ei = bi = 0
    total = len(utili) + len(bonus)
    for slot in range(total):
        if slot % 3 == 2 and bi < len(bonus):
            rotation.append(bonus[bi])
            bi += 1
        elif ei < len(utili):
            rotation.append(utili[ei])
            ei += 1
        elif bi < len(bonus):
            rotation.append(bonus[bi])
            bi += 1
    return rotation


ROTATION = build_rotation()


def get_item_for_day(day_index):
    return ROTATION[day_index % len(ROTATION)]


def format_daily_message(item):
    header = HEADERS.get(item.get("tipo", "utile"), HEADERS["utile"])
    lines = [
        header,
        "",
        "Pinyin: "      + item["pinyin"],
        "Pronuncia: "   + item["pronuncia"],
        "Significato: " + item["significato"],
        "",
        "Nota: " + item["esempio"],
    ]
    return "\n".join(lines)


def send_telegram_message(token, chat_id, text):
    url = "https://api.telegram.org/bot" + token + "/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    response = requests.post(url, data=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def parse_start_date(value):
    try:
        parts = value.split("-")
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except Exception as exc:
        raise ValueError("START_DATE non valida: " + value) from exc


def deliver(token, chat_id, text, dry_run, label):
    print("---- " + label + " ----")
    print(text)
    print("-------------------")
    if dry_run:
        return
    result = send_telegram_message(token, chat_id, text)
    if not result.get("ok"):
        raise RuntimeError("Telegram ha risposto con errore: " + str(result))


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    start_date_str = os.environ.get("START_DATE") or DEFAULT_START_DATE
    dry_run = os.environ.get("DRY_RUN", "").lower() in {"1", "true", "yes"}

    if not dry_run and (not token or not chat_id):
        print("Errore: imposta TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID.",
              file=sys.stderr)
        return 1

    start_date = parse_start_date(start_date_str)
    today = date.today()
    day_index = days_since_start(start_date, today)

    item = get_item_for_day(day_index)
    daily_message = format_daily_message(item)

    header = "[{0}] giorno {1} (rotazione: {2} voci)".format(
        today.isoformat(), day_index + 1, len(ROTATION))
    print(header)

    try:
        if day_index == 0:
            deliver(token, chat_id, GREETING, dry_run,
                    "messaggio 1 (saluto)")
            if not dry_run:
                time.sleep(1)
            deliver(token, chat_id, daily_message, dry_run,
                    "messaggio 2 (espressione cinese del giorno)")
        else:
            deliver(token, chat_id, daily_message, dry_run,
                    "messaggio del giorno")
    except requests.HTTPError as exc:
        print("Errore HTTP da Telegram: " + str(exc), file=sys.stderr)
        return 2
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if dry_run:
        print("DRY_RUN attivo: nessun invio effettuato.")
    else:
        print("Invio completato.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
