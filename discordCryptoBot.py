from discord import Client, Intents
from discord.ext import tasks
from requests import get

import os

FILENAME = os.path.abspath("prezzo_target.txt")
CHANNEL_ID = 800086577837637684
TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
FILENAME = os.path.abspath("prezzo_target.txt")

# Dichiarazione degli Intents
intents = Intents.default()
intents.messages = True

def get_prezzo_target():
    try:
        with open(FILENAME, 'r', encoding='utf-8') as f:
            prezzo_target = float(f.read())
    except (FileNotFoundError, ValueError):
        prezzo_target = 0  # Imposta un valore predefinito o gestisci l'errore in modo appropriato
    return prezzo_target


def set_prezzo_target(nuovo_prezzo_target):
    try:
        with open(FILENAME, 'w', encoding='utf-8') as f:
            print("prima del cambio")
            f.write(str(nuovo_prezzo_target))
            print("dopo il cambio")
    except PermissionError as pe:
        print(f"PermissionError: {pe}")
    except OSError as oe:
        print(f"OSError: {oe}")
    except Exception as e:
        print(f"Errore durante la scrittura nel file: {e}")



bot = Client(intents=intents)

@bot.event
async def on_ready():
    invia_quotazione.start()

@tasks.loop(hours=24)
async def invia_quotazione():
    response = get("https://api.kucoin.com/api/v1/market/stats?symbol=BTC-EUR")
    prezzo_attuale = float(response.json()['data']['buy'])
    canale = bot.get_channel(CHANNEL_ID)
    testo = f"il prezzo per un BTC è {prezzo_attuale}"
    if prezzo_attuale < get_prezzo_target(): 
        await canale.send(testo)
        await canale.send("E' arrivata l'ora di comprare!")
    else:
        await canale.send(testo)

@bot.event
async def on_message(message):
    autore = message.author
    testo = message.content
    canale = message.channel
    if autore == bot.user:
        return
    if testo.startswith('!prezzo'):
        print("Comando !prezzo rilevato")
        parts = testo.split()
        if len(parts) >= 2:
            print("Sufficienti argomenti dopo lo split")
            nuovo_prezzo_target_str = parts[1]
            try:
                print("Provo a convertire il prezzo")
                nuovo_prezzo_target = float(nuovo_prezzo_target_str)
                print("Conversione riuscita")
                await canale.send("Sto cambiando il prezzo.")
                set_prezzo_target(nuovo_prezzo_target)
                await canale.send(f"Ho aggiornato il prezzo target a {nuovo_prezzo_target} euro.")
            except ValueError as ve:
                print(f"Errore durante la conversione del prezzo: {ve}")
                await canale.send("Il formato del prezzo non è valido.")
        else:
            print("Comando !prezzo senza argomenti sufficienti")
            await canale.send("Il comando !prezzo richiede un valore.")
        return
    await canale.send(f"Ciao {autore.name}")
    await canale.send(f"Ti avviso non appena un BTC costa meno di {get_prezzo_target()} euro")
    await canale.send("per modificare il prezzo target usa il comando `!prezzo <nuovo_prezzo_target>`")
bot.run(TOKEN)
