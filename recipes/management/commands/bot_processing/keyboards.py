from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)

from .db_processing import get_or_create_user


class CustomCallbackData():
    def __init__(self, button, key, extra):
        self.button = button
        self.key = key
        self.extra = extra


def make_inline_dish_buttons(recipe,
                             another_extra,
                             favorite,
                             disliked):
    buttons = [
        [
            CustomCallbackData(
                button='Просмотреть рецепт полностью',
                key='show_full_recipe',
                extra=recipe.uuid
            )
        ],
        [
            CustomCallbackData(
                button='Выбрать другой рецепт',
                key='choose_another_recipe',
                extra=another_extra
            ),
        ]
    ]
    new_row = list()
    if recipe.uuid not in favorite:
        new_row.append(
            CustomCallbackData(
                button='Добавить в избранное',
                key='add_to_favorite',
                extra=recipe.uuid
            )
        )
    else:
        new_row.append(
            CustomCallbackData(
                button='Удалить из избранного',
                key='remove_from_favorite',
                extra=recipe.uuid
            )
        )
    if recipe.uuid not in disliked:
        new_row.append(
            CustomCallbackData(
                button='Добавить в стоп-лист',
                key='add_to_disliked',
                extra=recipe.uuid
            )
        )
    else:
        new_row.append(
            CustomCallbackData(
                button='Удалить из стоп-листа',
                key='remove_from_disliked',
                extra=recipe.uuid
            )
        )
    buttons.append(new_row)
    return buttons


def make_dish_types_buttons(dish_types):
    buttons = list()
    amount = len(dish_types)
    for i in range(0, amount - 1, 2):
        try:
            buttons.append([dish_types[i], dish_types[i + 1]])
        except IndexError:
            buttons.append([dish_types[i]])
    if amount % 2:
        buttons.append([dish_types[amount - 1]])
    return buttons


def main_keyboard(telegram_id: int,
                  header_buttons: list() = None,
                  footer_buttons: list() = None):
    user, _ = get_or_create_user(telegram_id)
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
                row_buttons.append(
                    InlineKeyboardButton(
                        text=button.button,
                        callback_data=f'{button.key}:{button.extra}'
                    )
                )
            buttons.append(row_buttons)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def await_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[['Загружаю данные...']],
        resize_keyboard=True
    )
