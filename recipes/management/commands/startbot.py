from django.core.management.base import BaseCommand
from environs import Env
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

from .bot_processing.db_processing import dish_types, recipes_titles
from .bot_processing.logger import make_logger
from .bot_processing.main_functions import (add_to_disliked, add_to_favorite,
                                            get_favorites,
                                            get_recipe, main_page, number_processing,
                                            remove_from_disliked,
                                            remove_from_favorite,
                                            view_dish_preview,
                                            view_full_recipe, donation_amount, change_user_lists_content)



AMOUNTS = [str(num) for num in range(100000)]


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
        dispatcher.add_handler(MessageHandler(Filters.text('Избранное'), get_favorites))

        dispatcher.add_handler(MessageHandler(Filters.text(dish_types), view_dish_preview))
        dispatcher.add_handler(MessageHandler(Filters.text(recipes_titles), view_dish_preview))

        dispatcher.add_handler(CallbackQueryHandler(view_full_recipe, pattern='show_full_recipe'))
        dispatcher.add_handler(CallbackQueryHandler(view_dish_preview, pattern='choose_another_recipe'))
        dispatcher.add_handler(CallbackQueryHandler(change_user_lists_content, pattern='add_to_favorite'))
        dispatcher.add_handler(CallbackQueryHandler(change_user_lists_content, pattern='add_to_disliked'))
        dispatcher.add_handler(CallbackQueryHandler(change_user_lists_content, pattern='remove_from_favorite'))
        dispatcher.add_handler(CallbackQueryHandler(change_user_lists_content, pattern='remove_from_disliked'))

        dispatcher.add_handler(CallbackQueryHandler(donation_amount, pattern='make_donation'))
        dispatcher.add_handler(MessageHandler(Filters.text(AMOUNTS), number_processing))

        updater.start_polling()
        updater.idle()
