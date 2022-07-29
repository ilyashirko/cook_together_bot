from typing import Union
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from .db_processing import get_dish_types_objects, get_or_create_user


class CustomCallbackData():
    def __init__(self, button, key, extra):
        self.button = button
        self.key = key
        self.extra = extra


def make_dish_types_buttons():
    buttons = list()
    all_dish_types = [
        dish_type.title
        for dish_type
        in get_dish_types_objects()
    ]
    for i in range(0, len(all_dish_types) - 1, 2):
        try:
            buttons.append([all_dish_types[i], all_dish_types[i + 1]])
        except IndexError:
            buttons.append([all_dish_types[i]])
    return buttons


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


def make_keyboard(header_buttons: list() = None,
                  main_buttons: list() = None,
                  footer_buttons: list() = None):
    buttons = list()
    if header_buttons:
        buttons.append(header_buttons)
    if main_buttons:
        buttons += main_buttons
    if footer_buttons:
        buttons.append(footer_buttons)
    buttons.append(['Написать в поддержку'])
    buttons.append(['Вернуться на главную'])
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )


def make_inline_keyboard(buttons_info):
    buttons = list()
    for row in buttons_info:
        if isinstance(row, CustomCallbackData):
            buttons.append([
                InlineKeyboardButton(
                    text=row.button,
                    callback_data=f'{row.key}:{row.extra}'
                )
            ])
        elif isinstance(row, (list, tuple)):
            row_buttons = list()
            for button in row:
                row_buttons.append([
                    InlineKeyboardButton(
                        text=button.button,
                        callback_data=f'{button.key}:{button.extra}'
                    )
                ])
            buttons.append(row_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def await_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[['Загружаю данные...']],
        resize_keyboard=True
    )