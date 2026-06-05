# Cinese per Jewel

Bot Telegram che ogni mattina invia a Jewel **una sola espressione cinese da
imparare**, scritta in alfabeto latino (pinyin + guida fonetica all'italiana),
in modo che si capisca subito come si pronuncia.

L'espressione del giorno può essere di tre tipi, che si alternano:
- **utile**: saluti, frasi pratiche, frasi da viaggio (~100 voci in `expressions.py`),
- **romantica**: frasi dolci da imparare in cinese (~20 voci in `bonuses.py`),
- **battuta**: modi di dire divertenti in cinese (~20 voci in `bonuses.py`).

Il primo giorno in assoluto arrivano **due messaggi**:

1) il saluto:

> Ciao Jewel, Marco pensa che tu sia bellissima lo sai? Ma bando alle ciance,
> impariamo un po' di cinese.

2) subito dopo, la prima espressione cinese del giorno.

Dai giorni successivi arriva un solo messaggio con l'espressione del giorno.

## Come funziona

- `expressions.py` contiene le espressioni utili.
- `bonuses.py` contiene frasi romantiche e battute in cinese.
- `main.py` costruisce una rotazione di 140 voci (pattern 2 utili : 1 bonus,
  con romantica/battuta alternate). Calcola quanti giorni sono passati da
  `START_DATE` e sceglie la voce corrispondente. Quando la lista finisce,
  riparte da capo.
- `.github/workflows/cinese.yml` è il workflow GitHub Actions che esegue
  `python main.py` una volta al giorno: lo script manda il messaggio e
  termina. **Gratis** (entro i 2000 min/mese del piano free, e illimitato per
  le repo pubbliche).

## Setup completo (GitHub Actions, gratis)

### 1. Crea il bot Telegram

1. Su Telegram apri `@BotFather` e manda `/newbot`.
2. Segui le istruzioni, scegli un nome e ottieni il **token**
   (es. `123456:ABC...`).
3. Jewel deve mandare almeno un messaggio al bot (o aggiungerlo a un gruppo),
   altrimenti Telegram non lascia che il bot scriva per primo.

### 2. Trova il chat_id di Jewel

Apri nel browser:

```
https://api.telegram.org/bot<IL_TUO_TOKEN>/getUpdates
```

dopo che Jewel ha scritto al bot. Nella risposta JSON cerca
`"chat":{"id": ...}`: quel numero è il `TELEGRAM_CHAT_ID`.

### 3. Crea la repo GitHub e carica i file

Carica nella **root** della repo questi file:

```
main.py
expressions.py
bonuses.py
requirements.txt
.gitignore
README.md
.github/workflows/cinese.yml
```

(Non caricare `__pycache__/` né file `.pyc`: il `.gitignore` li esclude
automaticamente se usi git da terminale.)

### 4. Configura i Secrets

Sulla pagina della repo: **Settings → Secrets and variables → Actions →
"New repository secret"**. Crea questi due secret:

- `TELEGRAM_BOT_TOKEN` → il token di @BotFather
- `TELEGRAM_CHAT_ID`   → il chat_id di Jewel

Opzionale: nello stesso pannello, sezione **Variables**, puoi aggiungere
`START_DATE` (es. `2026-06-06`) per fissare il "giorno 1". Se non la metti,
viene usato il default scritto in `main.py`.

### 5. Verifica con un avvio manuale

Vai sul tab **Actions** della repo → workflow "Cinese per Jewel" →
**Run workflow**. Se i secret sono corretti, Jewel riceve subito il messaggio.

### 6. Da domani parte da solo

Lo `schedule` predefinito è `0 7 * * *` UTC (≈ **09:00 italiane d'estate** /
**08:00 d'inverno**). Per cambiare orario modifica la riga `cron:` in
`.github/workflows/cinese.yml`. Sintassi: `minuto ora giorno mese giornoSettimana`,
sempre in **UTC** — togli un'ora rispetto all'ora italiana d'estate, due
d'inverno.

> Nota: GitHub Actions non garantisce la puntualità al secondo: il cron può
> partire con qualche minuto di ritardo (raramente fino a 15-20 min, ma di
> solito è entro 2-3 min). Per un messaggio del buongiorno è perfetto.

## Test in locale (facoltativo)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# anteprima senza inviare nulla
DRY_RUN=1 python main.py

# invio vero
export TELEGRAM_BOT_TOKEN="123456:ABC..."
export TELEGRAM_CHAT_ID="123456789"
python main.py
```

## Personalizzazione

- **Aggiungere espressioni utili**: appendi un nuovo dizionario in
  `EXPRESSIONS` dentro `expressions.py`.
- **Aggiungere frasi romantiche o battute in cinese**: appendi un nuovo
  dizionario in `BONUSES` dentro `bonuses.py` (campo `tipo`: `"romantica"`
  o `"battuta"`).
- **Cambiare il pattern di alternanza**: modifica `slot % 3 == 2` in
  `build_rotation()` (es. `% 2` = 1 bonus ogni 2 giorni).
- **Reset del conteggio**: cambia il secret/variabile `START_DATE` per
  ripartire dall'inizio.

Buono studio a Jewel.
