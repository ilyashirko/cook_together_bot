import re
import time

from .db_processing import get_dish_types_objects
from recipes.models import DishType, Recipe, Step, User

from .keyboards import (await_keyboard, main_keyboard,
                        make_dish_types_buttons, make_inline_dish_buttons,
                        make_inline_keyboard, make_keyboard)
from .messages import GET_RECIPE_MESSAGE, MAIN_TEXTS


def update_dish_types():
    global dish_types
    dish_types = [
        dish_type.title
        for dish_type
        in get_dish_types_objects()
    ]


def update_recipes_titles(recipes=Recipe.objects.all()):
    global recipes_titles
    recipes_titles = [recipe.title for recipe in recipes]


recipes_titles = update_recipes_titles()

dish_types = update_dish_types()


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
    global dish_types
    update_dish_types()
    dish_types_buttons = make_dish_types_buttons(dish_types)
    context.bot.send_message(
        text=GET_RECIPE_MESSAGE,
        chat_id=update.effective_chat.id,
        reply_markup=make_keyboard(main_buttons=dish_types_buttons)
    )


def dish_preview_message(recipe):
    full_time_str = extract_duration(recipe.full_time)
    stove_time_str = extract_duration(recipe.stove_time)
    allergens = [allergen.title for allergen in recipe.allergens.all()]
    message = str()
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


def view_dish_preview(update, context):
    global dish_types, recipes_titles
    update_recipes_titles()
    user = User.objects.filter(telegram_id=update.effective_chat.id) \
                       .prefetch_related(
                            'favorite_recipes',
                            'disliked_recipes'
                       ).first()

    disliked = [recipe.uuid for recipe in user.disliked_recipes.all()]

    try:
        _, dish_type = update.callback_query.data.split(':')
        recipe = DishType.objects.get(title=dish_type) \
                                 .recipes.exclude(uuid__in=disliked) \
                                 .order_by("?").first()
    except AttributeError:
        if update.message.text in dish_types:
            try:
                recipe = DishType.objects.get(title=update.message.text) \
                                         .recipes.exclude(uuid__in=disliked) \
                                         .order_by("?").first()
            except DishType.MultipleObjectsReturned:
                pass
        elif update.message.text in recipes_titles:
            try:
                recipe = Recipe.objects.get(title=update.message.text)
            except Recipe.MultipleObjectsReturned:
                pass

    if recipe:
        message = dish_preview_message(recipe)
        context.bot.send_photo(
            photo=open(f'{recipe.image}', 'rb'),
            chat_id=update.effective_chat.id,
            caption=recipe.title,
            reply_markup=main_keyboard(update.effective_user.id)
        )
        time.sleep(1)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            reply_markup=make_inline_keyboard(
                make_inline_dish_buttons(
                    recipe,
                    update.message.text if update.message else dish_type,
                    [recipe.uuid for recipe in user.favorite_recipes.all()],
                    disliked,
                )
            )
        )
    else:
        global dish_types
        update_dish_types()
        dish_types_buttons = make_dish_types_buttons(dish_types)
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


def add_to_favorite(update, context):
    user_id = update.effective_user.id

    user = User.objects.filter(telegram_id=update.effective_chat.id) \
                       .prefetch_related(
                            'favorite_recipes',
                            'disliked_recipes'
                       ).first()

    _, recipe_uuid = update.callback_query.data.split(':')
    recipe = Recipe.objects.get(uuid=recipe_uuid)

    if recipe not in user.favorite_recipes.all():
        user.favorite_recipes.add(recipe)
        user.save()
        message = f'Рецепт "{recipe.title}" добавлен в избранное.'
    else:
        message = f'Рецепт "{recipe.title}" уже в избранном.'

    if recipe in user.disliked_recipes.all():
        message += '\n\nРецепт также в списке "Стоп-лист", а значит ' \
                   'он сохранен, но в подборке показан не будет.'

    context.bot.send_message(
        chat_id=user_id,
        text=message,
        reply_markup=main_keyboard(user_id)
    )


def add_to_disliked(update, context):
    user_id = update.effective_user.id

    user = User.objects.filter(telegram_id=update.effective_chat.id) \
                       .prefetch_related(
                            'favorite_recipes',
                            'disliked_recipes'
                       ).first()

    _, recipe_uuid = update.callback_query.data.split(':')
    recipe = Recipe.objects.get(uuid=recipe_uuid)

    if recipe not in user.disliked_recipes.all():
        user.disliked_recipes.add(recipe)
        user.save()
        message = f'Рецепт "{recipe.title}" добавлен в стоп-лист.'
    else:
        message = f'Рецепт "{recipe.title}" уже в стоп-листе.'

    if recipe in user.favorite_recipes.all():
        message += '\n\nРецепт также в списке "Избранное", ' \
                   'а значит он сохранен, но в подборке показан не будет.'

    context.bot.send_message(
        chat_id=user_id,
        text=message,
        reply_markup=main_keyboard(user_id)
    )


def remove_from_favorite(update, context):
    user_id = update.effective_user.id

    user = User.objects.filter(telegram_id=update.effective_chat.id) \
                       .prefetch_related(
                            'favorite_recipes',
                            'disliked_recipes'
                       ).first()

    _, recipe_uuid = update.callback_query.data.split(':')
    recipe = Recipe.objects.get(uuid=recipe_uuid)

    if recipe in user.favorite_recipes.all():
        user.favorite_recipes.remove(recipe)
        user.save()
        message = f'Рецепт "{recipe.title}" удален из избранного.'
    else:
        message = f'Рецепт "{recipe.title}" уже нет в избранном.'

    context.bot.send_message(
        chat_id=user_id,
        text=message,
        reply_markup=main_keyboard(user_id)
    )


def remove_from_disliked(update, context):
    user_id = update.effective_user.id

    user = User.objects.filter(telegram_id=update.effective_chat.id) \
                       .prefetch_related(
                            'favorite_recipes',
                            'disliked_recipes'
                       ).first()

    _, recipe_uuid = update.callback_query.data.split(':')
    recipe = Recipe.objects.get(uuid=recipe_uuid)

    if recipe in user.disliked_recipes.all():
        user.disliked_recipes.remove(recipe)
        user.save()
        message = f'Рецепт "{recipe.title}" удален из стоп-листа.'
    else:
        message = f'Рецепт "{recipe.title}" уже нет в стоп-листе.'

    context.bot.send_message(
        chat_id=user_id,
        text=message,
        reply_markup=main_keyboard(user_id)
    )


def get_favorites(update, context):
    recipes = User.objects.get(telegram_id=update.effective_chat.id) \
                          .favorite_recipes.all()
    recipes_titles = [[recipe.title] for recipe in recipes]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Ваши любимые блюда внизу экрана. Можете выбрать любое.',
        reply_markup=make_keyboard(main_buttons=recipes_titles)
    )
