from recipes.management.commands.bot_processing.keyboards import main_keyboard
from .messages import HELLO_MESSAGE
from .db_processing import check_is_admin
from textwrap import dedent


def start(update, context):
    context.bot.send_message(
        text=HELLO_MESSAGE,
        chat_id=update.effective_chat.id,
        reply_markup=main_keyboard(update.effective_user.id)
    )