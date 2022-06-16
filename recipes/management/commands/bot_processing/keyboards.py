from telegram import ReplyKeyboardMarkup

from recipes.management.commands.bot_processing.db_processing import check_is_admin, get_or_create_user



def main_keyboard(telegram_id: int,
                  header_buttons: list() = None,
                  footer_buttons: list() = None):
    user, was_created = get_or_create_user(telegram_id)
    buttons = list()
    if header_buttons:
        buttons.append(header_buttons)
    buttons.append(['Выбрать рецепт'])
    if user.favorite_recipes:
        buttons.append(['Избранное'])
    if footer_buttons:
        buttons.append(footer_buttons)
    if user.is_admin:
        buttons.append(['ADMIN_CONSOLE'])
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )