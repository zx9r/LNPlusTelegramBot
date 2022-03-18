import json
import logging

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
            if not user or not user['authorized']:
                continue
            user_settings = user['settings']
            if user_settings['NOTIFICATIONS_STATUS'] != 'ON':
                continue
            for pending_swap in pending_swaps:
                if user_settings['MIN_CAPACITY'] <= pending_swap['capacity_sats'] <= user_settings['MAX_CAPACITY'] and \
                        user_settings['MIN_PLACES'] <= pending_swap['participant_max_count'] <= user_settings['MAX_PLACES'] and \
                        user_settings['MIN_PLACES_LEFT'] <= pending_swap['participant_waiting_for_count'] <= user_settings['MAX_PLACES_LEFT']:

                    if pending_swap['id'] not in user['notified_swaps']:
                        user['notified_swaps'].append(pending_swap['id'])
                        try:
                            bot.send_message(user_key, self.create_message(pending_swap))
                        except Unauthorized:
                            logger.info(f'Unable to send message to {user_settings} (Unauthorized)')
                            user['authorized'] = False
                        except Exception as e:
                            logger.exception(f"error sending alert to {user_key}", e)

    def create_message(self, pending_swap):
        message = f"""
New ring detected:
 
  Capacity: {pending_swap['capacity_sats']:,}
  Total places: {pending_swap['participant_max_count']}
  Places Left: {pending_swap['participant_waiting_for_count']}
  
  {pending_swap['web_url']}
"""
        return message


def retrieve_pending_swaps(num_swaps=50):
    pending_swaps_url = config.LNPLUS_API_URL + config.LNPLUS_API_LATEST_SWAPS + 'pending/' + str(num_swaps)

    response = requests.get(pending_swaps_url)
    pending_swaps = response.json()

    return pending_swaps


def retrieve_pending_swaps_scrapping():
    result = []
    page = 1
    url = config.LNPLUS_URL + config.LNPLUS_PENDING_PAGE1
    while True:
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        div_swaps = soup.find_all('div', class_='bg-white dark:bg-black rounded-br-2xl rounded-bl-xl shadow-md p-6')
        logger.debug(f'Found {len(div_swaps)} swaps open for application in page {page}')
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

        next_page = soup.find('a', rel='next')
        if not next_page:
            break

        page += 1
        url = config.LNPLUS_URL + next_page.get('href')

    return result


def lnplus_engine(context: CallbackContext):
    logger.debug("LN+ engine starting")
    pending_swaps = retrieve_pending_swaps()
    logger.debug(f'Retrieved {len(pending_swaps)} pending swaps')
    notifier = Notifier()
    notifier.notify(pending_swaps, context.dispatcher.user_data, context.bot)
    logger.debug("LN+ engine finished")
