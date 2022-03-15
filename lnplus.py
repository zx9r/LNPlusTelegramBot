import logging
import time

import requests
from bs4 import BeautifulSoup
from telegram.error import Unauthorized
from telegram.ext.callbackcontext import CallbackContext

import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Notifier:

    def __init__(self):
        pass

    def notify(self, pending_swaps, user_data, bot):
        for user_key in user_data:
            user = user_data[user_key]
            if not user['authorized']:
                continue
            user_config = user['config']
            if user_config['NOTIFICATIONS_STATUS'] != 'ON':
                continue
            for pending_swap in pending_swaps:
                if user_config['MIN_CAPACITY'] <= pending_swap['capacity'] <= user_config['MAX_CAPACITY'] and \
                        user_config['MIN_PLACES'] <= pending_swap['places_total'] <= user_config['MAX_PLACES'] and \
                        user_config['MIN_PLACES_LEFT'] <= pending_swap['places_left'] <= user_config['MAX_PLACES_LEFT']:

                    swap_id = pending_swap['swap_id']
                    notified = user['notified_swaps'].get(swap_id)
                    if not notified or notified != pending_swap:
                        user['notified_swaps'][swap_id] = pending_swap
                        try:
                            bot.send_message(user_key, self.create_message(pending_swap))
                        except Unauthorized:
                            logger.info(f'Unable to send message to {user_config} (Unauthorized)')
                            user['authorized'] = False
                        except Exception as e:
                            logger.exception(f"error sending alert to {user_key}", e)

    def create_message(self, pending_swap):
        message = f"""
New ring detected:
 
  Shape: {pending_swap['shape']}
  Capacity: {pending_swap['capacity']}
  Total places: {pending_swap['places_total']}
  Places Left: {pending_swap['places_left']}
  
  {config.LNPLUS_SWAP_URL}{pending_swap['swap_id']}
"""
        return message


def retrieve_pending_swaps():
    result = []
    response = requests.get(config.LNPLUS_URL)

    soup = BeautifulSoup(response.text, 'html.parser')
    div_swaps = soup.find_all('div', class_='bg-white dark:bg-black rounded-br-2xl rounded-bl-xl shadow-md p-6')
    logger.debug(f'Found {len(div_swaps)} swaps open for application')
    for div_swap in div_swaps:
        paragraphs = div_swap.find_all('p')
        shape = paragraphs[0].text.split()[0]
        capacity = int(paragraphs[1].text.split()[0].replace(',', ''))
        places = paragraphs[4].find_all('span')
        places_left = int(places[0].text)
        places_total = int(places[2].text)
        link = div_swap.find('a')
        swap_id = link.get('href').split('/')[-1]
        swap = {'swap_id': swap_id,
                'shape': shape,
                'capacity': capacity,
                'places_total': places_total,
                'places_left': places_left
                }
        result.append(swap)

    return result


def lnplus_engine(context: CallbackContext):
    logger.debug("LN+ engine starting")
    pending_swaps = retrieve_pending_swaps()
    notifier = Notifier()
    notifier.notify(pending_swaps, context.dispatcher.user_data, context.bot)
    logger.debug("LN+ engine finished")
