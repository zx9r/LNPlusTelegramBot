import logging

from telegram.ext import PicklePersistence
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.updater import Updater
from telegram.update import Update

import config
from lnplus import lnplus_engine
from telegram_token import TELEGRAM_TOKEN

logging.basicConfig(filename='debug.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info('Bot Starting...')

'''
bot name: LightningNetworkPlus
username: @LNPlus_bot
http://t.me/LNPlus_bot
'''

persistence = PicklePersistence(filename='bot_persistence')
updater = Updater(TELEGRAM_TOKEN, persistence=persistence, use_context=True)
logger.debug('Loaded persistence user data')
logger.debug(persistence.get_user_data())


def start(update: Update, context: CallbackContext):
    logger.debug(f'start command called from {update.effective_user}')

    if context.user_data.get('effective_user'):
        reply_text = 'Bot was already started'
    else:
        context.user_data['effective_user'] = update.effective_user
        context.user_data['authorized'] = True
        context.user_data['config'] = {
            'MIN_CAPACITY': config.MIN_CAPACITY,
            'MAX_CAPACITY': config.MAX_CAPACITY,
            'MIN_PLACES': config.MIN_PLACES,
            'MAX_PLACES': config.MAX_PLACES,
            'MIN_PLACES_LEFT': config.MIN_PLACES_LEFT,
            'MAX_PLACES_LEFT': config.MAX_PLACES_LEFT,
            'NOTIFICATIONS_STATUS': 'ON'
        }
        context.user_data['notified_swaps'] = {}
        reply_text = "Welcome to the LightningNetworkPlus Notification Bot. Type /help to see the list of commands"
    logger.debug(context.user_data)
    update.message.reply_text(reply_text)


def help(update: Update, context: CallbackContext):
    logger.debug(f'help command called from {update.effective_user}')

    help_message = '''
/set_notification_status <on | off> - Turn notifications on/off
/set_min_capacity <min_capacity> - Set the minimum capacity of the rings to be notified
/set_max_capacity <max_capacity> - Set the maximum capacity of the rings to be notified
/set_min_places <min_places> - Set the minimum number of places of the rings to be notified
/set_max_places <max_places> - Set the maximum number of places of the rings to be notified
/set_min_places_left <min_places_left> - Set the minimum number of places left of the rings to be notified
/set_max_places_left <max_places_left> - Set the maximum number of places left of the rings to be notified
/show_config - Show the actual configuration
'''
    update.message.reply_text(help_message)


def show_config(update: Update, context: CallbackContext):
    logger.debug(f'show_config command called from {update.effective_user}')

    user_config = context.user_data['config']
    config_message = f'Notification status: {user_config["NOTIFICATIONS_STATUS"]}\n'
    config_message += f'min_capacity: {user_config["MIN_CAPACITY"]}\n'
    config_message += f'max_capacity: {user_config["MAX_CAPACITY"]}\n'
    config_message += f'min_places: {user_config["MIN_PLACES"]}\n'
    config_message += f'max_places: {user_config["MAX_PLACES"]}\n'
    config_message += f'min_places_left: {user_config["MIN_PLACES_LEFT"]}\n'
    config_message += f'max_places_left: {user_config["MAX_PLACES_LEFT"]}\n'
    update.message.reply_text(config_message)


def set_min_capacity(update: Update, context: CallbackContext):
    try:
        min_capacity = int(update.message.text.split()[1])
        context.user_data['config']['MIN_CAPACITY'] = min_capacity
        response = f'min_capacity set to {min_capacity}'
    except:
        response = 'Invalid value'
    update.message.reply_text(response)


def set_max_capacity(update: Update, context: CallbackContext):
    try:
        max_capacity = int(update.message.text.split()[1])
        context.user_data['config']['MAX_CAPACITY'] = max_capacity
        response = f'max_capacity set to {max_capacity}'
    except:
        response = 'Invalid value'
    update.message.reply_text(response)


def set_min_places(update: Update, context: CallbackContext):
    try:
        min_places = int(update.message.text.split()[1])
        context.user_data['config']['MIN_PLACES'] = min_places
        response = f'min_places set to {min_places}'
    except:
        response = 'Invalid value'
    update.message.reply_text(response)


def set_max_places(update: Update, context: CallbackContext):
    try:
        max_places = int(update.message.text.split()[1])
        context.user_data['config']['MAX_PLACES'] = max_places
        response = f'max_places set to {max_places}'
    except:
        response = 'Invalid value'
    update.message.reply_text(response)


def set_min_places_left(update: Update, context: CallbackContext):
    try:
        min_places_left = int(update.message.text.split()[1])
        context.user_data['config']['MIN_PLACES_LEFT'] = min_places_left
        response = f'min_places_left set to {min_places_left}'
    except:
        response = 'Invalid value'
    update.message.reply_text(response)


def set_max_places_left(update: Update, context: CallbackContext):
    try:
        max_places_left = int(update.message.text.split()[1])
        context.user_data['config']['MAX_PLACES_LEFT'] = max_places_left
        response = f'max_places_left set to {max_places_left}'
    except:
        response = 'Invalid value'
    update.message.reply_text(response)


def set_notification_status(update: Update, context: CallbackContext):
    try:
        status = update.message.text.split()[1].upper()
        notification_on = status == '1' or status == 'ON' or status == 'TRUE'
        if notification_on:
            context.user_data['config']['NOTIFICATIONS_STATUS'] = 'ON'
            response = f'Notification status is now ON'
        else:
            notification_off = status == '0' or status == 'OFF' or status == 'OF' or status == 'FALSE'
            if notification_off:
                context.user_data['config']['NOTIFICATIONS_STATUS'] = 'OFF'
                response = f'Notification status is now OFF'
            else:
                response = 'Invalid value'
    except:
        response = 'Invalid value'

    update.message.reply_text(response)


def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Sorry '%s' is not a valid command" % update.message.text)


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text("Sorry I can't recognize you , you said '%s'" % update.message.text)


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('show_config', show_config))
updater.dispatcher.add_handler(CommandHandler('set_min_capacity', set_min_capacity))
updater.dispatcher.add_handler(CommandHandler('set_max_capacity', set_max_capacity))
updater.dispatcher.add_handler(CommandHandler('set_min_places', set_min_places))
updater.dispatcher.add_handler(CommandHandler('set_max_places', set_max_places))
updater.dispatcher.add_handler(CommandHandler('set_min_places_left', set_min_places_left))
updater.dispatcher.add_handler(CommandHandler('set_max_places_left', set_max_places_left))
updater.dispatcher.add_handler(CommandHandler('set_notification_status', set_notification_status))
# Filters out unknown commands
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))
# Filters out unknown messages.
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

updater.job_queue.run_repeating(lnplus_engine, interval=config.POLL_INTERVAL)

updater.start_polling()
updater.idle()
