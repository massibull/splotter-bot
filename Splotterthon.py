from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from google.oauth2.service_account import Credentials
import gspread

# Scope di autorizzazione per Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

# Caricamento credenziali e apertura foglio Google Sheets
creds = Credentials.from_service_account_file("credenziali.json", scopes=SCOPES)
client = gspread.authorize(creds)
spreadsheet = client.open("Splotterthon 2025")
sheet = spreadsheet.sheet1

TOKEN = "7744297660:AAG-o1mbwk1nD_tWGRrWgC2Xv9nvfTQFpdk"

def get_classifica_generale():
    titolo = sheet.cell(1, 1).value
    all_values = sheet.get_all_values()
    header_row_index = 3  # riga 4, indice 3 (zero-based)
    header = all_values[header_row_index]
    data = all_values[header_row_index + 1:]
    records = [dict(zip(header, row)) for row in data if any(row)]
    return titolo, records

def get_classifica_antiquity():
    antiquity_sheet = spreadsheet.worksheet("Antiquity")
    titolo = antiquity_sheet.cell(1, 1).value
    all_values = antiquity_sheet.get_all_values()
    header_row_index = 5  # riga 6, indice 5 (zero-based)
    header = all_values[header_row_index][:5]  # colonne A-E
    data = all_values[header_row_index + 1:]
    records = [dict(zip(header, row[:5])) for row in data if any(row[:5])]
    return titolo, records

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messaggio = (
        "🤖 Ciao! Questo è il Bot della Splotterthon\n"
        "Chiedimi quello che vuoi sapere sullo stato della splotterthon.\n"
        "Sono ancora in sviluppo, quindi potrei sbagliarmi.\n"
        "Qui trovi il tabellone aggiornato dello Splotterthon 2025:\n"
        "https://tinyurl.com/Splotterthon-2025\n\n"
        "Se noti qualcosa che non va scrivi al mio creatore @massibull\n"
        "Usa il comando /help per altre informazioni."
    )
    await update.message.reply_text(messaggio)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messaggio = (
        "Ecco i comandi ad oggi disponibili:\n"
        "/start - Avvia il bot e mostra le informazioni base\n"
        "/classifica - Mostra la classifica generale (verrà aggiornata via via che finiscono i vari tornei)\n"
        "/antiquity - Mostra la classifica del torneo Antiquity"
    )
    await update.message.reply_text(messaggio)

async def classifica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    titolo, records = get_classifica_generale()
    testo = f"📊 {titolo}:\n\n"
    for r in records:
        testo += f"{r.get('Classifica', '?')} - {r.get('Nome', '?')} : {r.get('Punti', '?')} punti, {r.get('Vittorie', '?')} vittorie\n"
    await update.message.reply_text(testo)

async def antiquity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    titolo, records = get_classifica_antiquity()
    testo = f"📊 {titolo} - Classifica Antiquity:\n\n"

    for r in records:
        posizione = r.get('Classifica', '').strip()
        # Stampa solo righe con posizione numerica (esclude righe tipo "CALENDARIO" ecc)
        if posizione.isdigit():
            nome = r.get('Nome', '?')
            punti = r.get('Punti', '?')
            vittorie = r.get('Vittorie', '?')
            testo += f"{posizione} - {nome} : {punti} punti, {vittorie} vittorie\n"

    await update.message.reply_text(testo)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("classifica", classifica))
    app.add_handler(CommandHandler("antiquity", antiquity))
    print("Bot Splotterthon avviato...")
    app.run_polling()

if __name__ == '__main__':
    main()