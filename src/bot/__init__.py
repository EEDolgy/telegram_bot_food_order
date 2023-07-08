from sqlalchemy.orm import sessionmaker
from telegram import KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove, Update, WebAppInfo, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, \
    MessageHandler, filters, CallbackQueryHandler

from src.bot.database import get_meta_info
# from src.bot.googledrive_exchange.Google_Drive \
#     import get_data_from_google_drive, add_data_to_db

def run_bot():
    with open('bot/user_data/token.txt', 'r') as f:
        TOKEN = f.read()

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("i_am_mama", mama_stuff))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("last_order", last_order))
    application.add_handler(MessageHandler(
        filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    # application.add_handler(CallbackQueryHandler(mama_commands))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

# # Enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
# logger = logging.getLogger(__name__)


MAMA_ACTIONS = {'Update menu': 'Загрузить новое меню',
                'Update Google Drive': 'Обновить таблицы заказов и клиентов'}


async def start(update: Update, context) -> None:
    """Send a message with a button that opens the web app."""

    text = get_meta_info('hello_text')

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Посмотреть меню и сделать заказ",
                web_app=WebAppInfo("https://286c-176-221-140-194.eu.ngrok.io/"),
            ),
            resize_keyboard=True
        ),
    )


async def mama_stuff(update: Update, context) -> None:
    permissions = get_meta_info('permissions')
    permissions = permissions.split(', ')
    user = update.effective_user

    if user.username in permissions:
        await update.message.reply_text(
            f"Здравствуйте, Нина!"
        )
        reply_keyboard = [[InlineKeyboardButton(val, callback_data=key)] for key, val in MAMA_ACTIONS.items()]
        await update.message.reply_text(
            rf"Что Вы хотите сделать?",
            reply_markup=InlineKeyboardMarkup(reply_keyboard)
        )
    else:
        if user.first_name:
            first_name = user.first_name
        else:
            first_name = ''
        if user.last_name:
            last_name = user.last_name
        else:
            last_name = ''
        await update.message.reply_text(
            f"Вы не мама Нина, Вы - {first_name} {last_name} :) "
        )


# async def mama_commands(update: Update, context) -> None:
#     action = update.callback_query.data
#
#     if action == 'Update menu':
#         await update.effective_message.reply_text(
#             "Подождите, меню обновляется..."
#         )
#         get_data_from_google_drive()
#         await update.effective_message.reply_text(
#             'Новое меню загружено в базу данных!'
#         )
#     elif action == 'Update Google Drive':
#         await update.effective_message.reply_text(
#             "Подождите, данные загружаются на диск..."
#         )
#         add_data_to_db()
#         await update.effective_message.reply_text(
#             'Данные о пользователях и заказах обновлены!'
#         )


async def last_order(update: Update, context) -> None:
    await update.message.reply_text(
        'У вас нет оформленных заказов за прошлый раз'
    )


# Handle incoming WebAppData
async def web_app_data(update: Update, context) -> None:
    pass
    # username = update.effective_user.username
    # order_date = update.message.date
    #
    # data = update.effective_message.web_app_data.data
    # data = json.loads(data)
    # data['username'] = username
    # data['order_date'] = (order_date + dt.timedelta(hours=4)).strftime('%Y-%m-%d %H:%M')
    #
    # pprint(data)
    #
    # await update.message.reply_text(
    #         rf"Ваш заказ записан!"
    # )
    #
    # add_order(data)