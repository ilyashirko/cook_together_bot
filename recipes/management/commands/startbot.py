from environs import Env

from django.core.management.base import BaseCommand
from .bot_processing.logger import make_logger
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)
from .bot_processing.main_functions import start


class Command(BaseCommand):
    help = "Telegram bot"

    def handle(self, *args, **kwargs):
        env = Env()
        env.read_env()
        
        log = make_logger(env)

        updater = Updater(token=env.str('TELEGRAM_BOT_TOKEN'), use_context=True)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', start))

        updater.start_polling()
        updater.idle()
