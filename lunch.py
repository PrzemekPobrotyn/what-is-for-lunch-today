import sys

import facebook
import requests

from config.config import (restaurants,
                           posts_limit,
                           keywords,
                           slack_webhook)
from config.credentials import (USER_TOKEN)

import utils




def start_graph(access_token=USER_TOKEN):
    graph = facebook.GraphAPI(access_token=access_token)
    return graph


def find_todays_lunch_all_restaurants(
        graph, restaurants=restaurants, keywords=keywords, limit=posts_limit):
    """
    Finds a lunch posts from all restaruants.
    :param graph: an authenticated facebook graph API object
    :param restaurants, a dict of restaurants for which to fetch lunches
    :param keywords, list of keywords by which to recognise a post about lunch
    :param limit, int, number of posts to fetch in order to search for lunch
    :return: lunches, dict where keys are restaurants names and values are
    strs - contents of fb posts with restaurants lunch offers
    """

    lunches = {}
    for rest_name, rest_id in restaurants.items():
        resp = utils.fetch_restaurant_posts(graph, rest_id, limit)
        lunches[rest_name] = utils.find_todays_lunch_single_restaurant(
            rest_name, resp, keywords)
    return lunches


def send_menu(lunches_dict, mailing_list):
    """Sends many to all addresses from the mailing list."""
    if utils.check_lunches(lunches_dict):
        message = utils.lunches_dict_to_html(lunches_dict)
        utils.send_mail(message, to=mailing_list)
        return True
    else:
        return False


def post_to_slack(lunches_dict, webhook=slack_webhook):
    if utils.check_lunches(lunches_dict):
        post = utils.lunches_dict_to_slack_post(lunches_dict)
        requests.post(webhook, json={'text': post})
        return True
    else:
        return False


def exit_script(bool):
    """
    Exits the script with code 1 if at least one restaurant hasn't posted its
    lunch yet.
    :param bool: boolean, return value of _send_mail
    """
    if not bool:
        print("One of the restaurants has not posted about today's lunch yet")
        print("Try again later.")
        sys.exit(1)
    else:
        print('Successfully found and mailed lunch menus on {}. '
              'Enjoy your meal!'.format(utils.date_today()))


if __name__ == '__main__':
    graph = start_graph()
    lunches = find_todays_lunch_all_restaurants(graph)
    b = post_to_slack(lunches)
    # b = send_menu(lunches, mailing_list)
    exit_script(b)


#TODO: add unittests
#TODO: change the logic of the script to post each lunch independently of the others
