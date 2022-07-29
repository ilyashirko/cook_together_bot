import re
import time

from recipes.models import DishType, Recipe, Step

from .keyboards import (CustomCallbackData, await_keyboard, main_keyboard,
                        make_dish_types_buttons, make_inline_keyboard,
                        make_keyboard)
from .messages import GET_RECIPE_MESSAGE, MAIN_TEXTS


class NoMatches(Exception):
    def __init__(self, text):
        self.text = text
    
    def __str__(self):
        return self.text


def extract_duration(duration):
    extracted_duration = [
        int(num)
        for num
        in re.split(' days, |:', str(duration))
    ]
    message = str()
    units = ('дн.', 'ч.', 'м.', 'с.')
    for _ in range(len(extracted_duration)):
        if len(extracted_duration) == 3 and extracted_duration[_]:
            message += f'{extracted_duration[_]} {units[_ + 1]} '
        elif extracted_duration[_]:
            message += f'{extracted_duration[_]} {units[_]} '
    return message


def main_page(update, context):
    context.bot.send_message(
        text=MAIN_TEXTS[update.message.text.lower()],
        chat_id=update.effective_chat.id,
        reply_markup=main_keyboard(update.effective_user.id)
    )


def get_recipe(update, context):
    dish_types_buttons = make_dish_types_buttons()
    context.bot.send_message(
        text=GET_RECIPE_MESSAGE,
        chat_id=update.effective_chat.id,
        reply_markup=make_keyboard(main_buttons=dish_types_buttons)
    )


def dish_preview_message(recipe):
    full_time_str = extract_duration(recipe.full_time)
    stove_time_str = extract_duration(recipe.stove_time)
    allergens = [allergen.title for allergen in recipe.allergens.all()]
    message = f'{recipe.title}'
    if allergens:
        message += ('\n\nВНИМАНИЕ!\nВ рецепте присутствуют аллергены:')
        for allergen in allergens:
            message += f'\n   {allergen}'
    message += (
        f'\n\n{recipe.description}'
        f'\n\nВремя приготовления: {full_time_str}'
        f'\nВремя "у плиты": {stove_time_str}'
    )
    return message


def view_random_dish_preview(update, context):
    recipe = DishType.objects.get(title=update.message.text).recipes.order_by("?").first()
    if recipe:
        message = dish_preview_message(recipe)
        context.bot.send_photo(
            photo=open(f'{recipe.image}', 'rb'),
            chat_id=update.effective_chat.id,
            caption=message,
            reply_markup=make_inline_keyboard(
                (
                    CustomCallbackData(
                        button='Просмотреть рецепт полностью',
                        key='show_full_recipe',
                        extra=recipe.uuid
                    ),
                )
            )
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Что хочешь сделать с этим рецептом?',
            reply_markup=main_keyboard(update.effective_user.id)
        )
    else:
        dish_types_buttons = make_dish_types_buttons()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Увы, нет доступных рецептов данной категории',
            reply_markup=make_keyboard(main_buttons=dish_types_buttons)
        )

def view_full_recipe(update, context):
    recipe_uuid = update.callback_query.data.split(':')[1]
    recipe = Recipe.objects.get(uuid=recipe_uuid)
    steps = Step.objects.filter(recipe=recipe)
    for num, step in enumerate(steps):
        context.bot.send_photo(
            photo=open(f'media/photo/{recipe.title}/{num + 1}.jpg', 'rb'),
            chat_id=update.effective_chat.id,
            caption=step.description,
            reply_markup=await_keyboard()
        )
        time.sleep(0.5)
    if steps:
        message = 'Приятного аппетита!'
    else:
        message = 'Извини, пошаговая инструкция недоступна.'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=main_keyboard(update.effective_user.id)
    )
