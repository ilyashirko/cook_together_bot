from django.core.management.base import BaseCommand
from environs import Env
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

from .bot_processing.logger import make_logger
from .bot_processing.main_functions import (add_to_disliked, add_to_favorite,
                                            dish_types, get_favorites,
                                            get_recipe, main_page,
                                            recipes_titles,
                                            remove_from_disliked,
                                            remove_from_favorite,
                                            view_dish_preview,
                                            view_full_recipe)


class Command(BaseCommand):
    help = "Telegram bot"

    def handle(self, *args, **kwargs):
        env = Env()
        env.read_env()

        log = make_logger(env)

        updater = Updater(
            token=env.str('TELEGRAM_BOT_TOKEN'),
            use_context=True
        )
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', main_page))
        dispatcher.add_handler(MessageHandler(Filters.text('Вернуться на главную'), main_page))

        dispatcher.add_handler(MessageHandler(Filters.text('Выбрать рецепт'), get_recipe))
        dispatcher.add_handler(MessageHandler(Filters.text(dish_types), view_dish_preview))
        dispatcher.add_handler(MessageHandler(Filters.text(recipes_titles), view_dish_preview))

        dispatcher.add_handler(MessageHandler(Filters.text('Избранное'), get_favorites))

        dispatcher.add_handler(CallbackQueryHandler(view_full_recipe, pattern='show_full_recipe'))
        dispatcher.add_handler(CallbackQueryHandler(view_dish_preview, pattern='choose_another_recipe'))
        dispatcher.add_handler(CallbackQueryHandler(add_to_favorite, pattern='add_to_favorite'))
        dispatcher.add_handler(CallbackQueryHandler(add_to_disliked, pattern='add_to_disliked'))
        dispatcher.add_handler(CallbackQueryHandler(remove_from_favorite, pattern='remove_from_favorite'))
        dispatcher.add_handler(CallbackQueryHandler(remove_from_disliked, pattern='remove_from_disliked'))

        updater.start_polling()
        updater.idle()
