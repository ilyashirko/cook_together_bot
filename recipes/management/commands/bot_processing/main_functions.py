import re
import time

from recipes.models import DishType, Donate, Recipe, Step, User
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from .db_processing import dish_types, recipes_titles, update_recipes_titles
from .keyboards import (await_keyboard, main_keyboard, make_dish_types_buttons,
                        make_inline_dish_buttons, make_inline_keyboard,
                        make_keyboard)
from .messages import GET_RECIPE_MESSAGE, MAIN_TEXTS


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
    favorites = [recipe.uuid for recipe in user.favorite_recipes.all()]

    try:
        _, dish_type = update.callback_query.data.split(':')
        recipe = DishType.objects.get(title=dish_type) \
                                 .recipes.exclude(uuid__in=disliked) \
                                 .order_by("?").first()
    except DishType.MultipleObjectsReturned:
        pass
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

    assert isinstance(recipe, Recipe)

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
                    recipe.uuid in favorites,
                    recipe.uuid in disliked,
                )
            )
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


def find_inline_button(callback_buttons: list,
                       title_to_find: str) -> InlineKeyboardButton:
    buttons = sum(callback_buttons, [])
    for button in buttons:
        print(button.text)
        if button.text == title_to_find:
            return button


def change_user_lists_content(update, context):
    current_callback, recipe_uuid = update.callback_query.data.split(":")
    user = User.objects.filter(telegram_id=update.effective_chat.id) \
                       .prefetch_related(
                            'favorite_recipes',
                            'disliked_recipes'
                       ).first()
    recipe = Recipe.objects.get(uuid=recipe_uuid)
    methods = {
        'add_to_favorite': {
            'condition': recipe not in user.favorite_recipes.all(),
            'action': user.favorite_recipes.add(recipe),
            'current_text': 'Добавить в избранное',
            'new_text': 'Удалить из избранного',
            'new_callback': 'remove_from_favorite'
        },
        'add_to_disliked': {
            'condition': recipe not in user.disliked_recipes.all(),
            'action': user.disliked_recipes.add(recipe),
            'current_text': 'Добавить в стоп-лист',
            'new_text': 'Удалить из стоп-листа',
            'new_callback': 'remove_from_disliked'
        },
        'remove_from_favorite': {
            'condition': recipe not in user.favorite_recipes.all(),
            'action': user.favorite_recipes.add(recipe),
            'current_text': 'Удалить из избранного',
            'new_text': 'Добавить в избранное',
            'new_callback': 'add_to_favorite'
        },
        'remove_from_disliked': {
            'condition': recipe not in user.disliked_recipes.all(),
            'action': user.disliked_recipes.add(recipe),
            'current_text': 'Удалить из стоп-листа',
            'new_text': 'Добавить в стоп-лист',
            'new_callback': 'add_to_disliked'
        }
    }
    
    if methods[current_callback]['condition']:
        methods[current_callback]['action']
        user.save()
    
    inline_to_change = find_inline_button(
        update.effective_message.reply_markup.inline_keyboard,
        methods[current_callback]['current_text']
    )
    inline_to_change.text = methods[current_callback]['new_text']
    inline_to_change.callback_data = inline_to_change.callback_data \
        .replace(
            current_callback,
            methods[current_callback]['new_callback']
        )
    
    context.bot.editMessageReplyMarkup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=InlineKeyboardMarkup(
            update.effective_message.reply_markup.inline_keyboard
        )
    )
    update.callback_query.data = f'{methods[current_callback]["new_callback"]}:{recipe_uuid}'



def add_to_favorite(update, context):
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
    
    favorite_inline = find_inline_button(
        update.effective_message.reply_markup.inline_keyboard,
        'Добавить в избранное'
    )
    
    favorite_inline.text = 'Удалить из избранного'
    favorite_inline.callback_data = favorite_inline.callback_data \
        .replace('add_to_favorite', 'remove_from_favorite')
    
    context.bot.editMessageReplyMarkup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=InlineKeyboardMarkup(
            update.effective_message.reply_markup.inline_keyboard
        )
    )


def add_to_disliked(update, context):
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

    favorite_inline = find_inline_button(
        update.effective_message.reply_markup.inline_keyboard,
        'Добавить в стоп-лист'
    )
    
    favorite_inline.text = 'Удалить из стоп-листа'
    favorite_inline.callback_data = favorite_inline.callback_data \
        .replace('add_to_disliked', 'remove_from_disliked')
    
    context.bot.editMessageReplyMarkup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=InlineKeyboardMarkup(
            update.effective_message.reply_markup.inline_keyboard
        )
    )


def remove_from_favorite(update, context):
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
    
    favorite_inline = find_inline_button(
        update.effective_message.reply_markup.inline_keyboard,
        'Удалить из избранного'
    )
    
    favorite_inline.text = 'Добавить в избранное'
    favorite_inline.callback_data = favorite_inline.callback_data \
        .replace('remove_from_favorite', 'add_to_favorite')
    
    context.bot.editMessageReplyMarkup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=InlineKeyboardMarkup(
            update.effective_message.reply_markup.inline_keyboard
        )
    )


def remove_from_disliked(update, context):
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

    disliked_inline = find_inline_button(
        update.effective_message.reply_markup.inline_keyboard,
        'Удалить из стоп-листа'
    )
    
    disliked_inline.text = 'Добавить в стоп-лист'
    disliked_inline.callback_data = disliked_inline.callback_data \
        .replace('remove_from_disliked', 'add_to_disliked')
    
    context.bot.editMessageReplyMarkup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=InlineKeyboardMarkup(
            update.effective_message.reply_markup.inline_keyboard
        )
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


def donation_amount(update, context):
    Donate.objects.get_or_create(user='User')
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Какую сумму вы хотели бы задонатить?',
        reply_markup=make_keyboard(main_buttons=recipes_titles)
    )

def number_processing(update, context):
    donate = Donate.objects.get(user='User', amount=None)
    if donate is None:
        return
    donate.amount = int(update.message.text)