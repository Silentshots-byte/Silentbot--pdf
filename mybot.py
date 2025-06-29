import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from fpdf import FPDF

# Стани розмови
COURT, NAME, ADDRESS, PHONE, EMAIL, CASE_NUMBER, DATE = range(7)

# Дані користувача
user_data = {}

# Налаштування логів
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Старт бота
async def start(update: Update, context):
    await update.message.reply_text("Привіт! Давай створимо заяву. Введи назву суду:")
    return COURT
async def court_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data['court'] = update.message.text
    await update.message.reply_text("Введи своє ПІБ:")
    return NAME

async def name_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data['name'] = update.message.text
    await update.message.reply_text("Введи адресу:")
    return ADDRESS

async def address_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data['address'] = update.message.text
    await update.message.reply_text("Введи номер телефону:")
    return PHONE

async def phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data['phone'] = update.message.text
    await update.message.reply_text("Введи email:")
    return EMAIL

async def email_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data['email'] = update.message.text
    await update.message.reply_text("Введи номер справи:")
    return CASE_NUMBER

async def case_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data['case_number'] = update.message.text
    await update.message.reply_text("Введи дату заяви (напр. 17.06.2025):")
    return DATE

async def date_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data['date'] = update.message.text
    file_path = generate_pdf(user_data)
    await update.message.reply_text("Готово! Ось твій PDF ⬇️")
    await update.message.reply_document(document=open(file_path, "rb"))
    return ConversationHandler.END

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.add_page()

    content = f"""До: {data['court']}
Від: {data['name']}
Адреса: {data['address']}
Тел.: {data['phone']}
Email: {data['email']}

У справі № {data['case_number']}

ЗАЯВА

Прошу надати можливість ознайомитися з матеріалами справи №{data['case_number']}, а саме:
- копіями процесуальних документів,
- постанов суду (за наявності),
- протоколами судових засідань,
- іншими матеріалами справи.

Прошу, за можливості, надати копії в електронному вигляді на вказану електронну адресу.

{data['name']}
{data['date']}"""

    pdf.multi_cell(0, 10, content)
    output_path = "oznajomlennya_result.pdf"
    pdf.output(output_path)
    return output_path

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Операцію скасовано.")
    return ConversationHandler.END

# Запуск бота
def main():
    app = ApplicationBuilder().token("ВСТАВ_ТУТ_СВІЙ_ТОКЕН").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            COURT: [MessageHandler(filters.TEXT & ~filters.COMMAND, court_input)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_input)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_input)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_input)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_input)],
            CASE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, case_input)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
