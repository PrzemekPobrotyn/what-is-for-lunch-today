import datetime
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import facebook
import requests
from requests.exceptions import RequestException

from config.config import (posts_limit,
                           keywords,
                           days_list,
                           weekly_menus)
from config.credentials import (email_address,
                                email_password,
                                admin_email)


class NetworkError(Exception):
    """
    Exception raised when there are problems connecting to facebook,
    Slack or email.
    """
    pass


# functions for checking if conditions are met

def check_lunches(lunches_dict):
    """Checks if every restaurant posted their lunch already."""
    if all(lunches_dict.values()):
        return True
    else:
        return False


def is_about_lunch(post, keywords):
    return any(word in post['message'] for word in keywords)


def date_today():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")


def is_today(post):
    return post['created_time'][:10] == date_today()


# functions for fetching menus from facebook

def find_todays_lunch_single_restaurant(rest_name, resp, keywords=keywords):
    message = None
    for post in resp['posts']['data']:
        try:
            # first non empty message about lunch from right day or weekly menu
            if (is_about_lunch(post, keywords) and
                    (is_today(post) or rest_name in weekly_menus)
                    and not message):
                message = post['message']
        except KeyError:
            pass

    if rest_name in weekly_menus and message:
        weekday = datetime.datetime.now().weekday()
        message = single_day_from_week_menu(message, weekday)

    return message


def fetch_restaurant_posts(graph, restaurant_id, limit=posts_limit):

    try:
        resp = graph.get_object(
            id=restaurant_id,
            fields='posts.limit({})'.format(limit))
    except (facebook.GraphAPIError, RequestException) as e:
        message = "An error occurred while attempting to fetch facebook posts:"
        message += str(e)
        send_mail(message=message, to=admin_email)
        print('\n terminating the script...')
        raise NetworkError

    return resp


def single_day_from_week_menu(message, day):
    """
    This implementation is specific to the way Centrum presents their
    weekly lunch offer.
    It most likely will produce rubbish for other restaurants.
    """
    days_lunch = ''
    day_seen = False  # indicator if we started looping over the correct day
    for line in message.split('\n'):
        if days_list[day+1] in line:
            return days_lunch
        elif day_seen:
            days_lunch += ('\n' + line)
        elif days_list[day] in line:
            days_lunch += line
            day_seen = True

    return days_lunch


# functions for posting to slack

def lunches_dict_to_slack_post(lunches_dict):
    post = ''
    for restaurant in lunches_dict.keys():
        post += ('*' + restaurant.upper() + '*')
        post += '\n\n'
        post += lunches_dict[restaurant]
        post += '\n\n\n'
    return post


def post_to_slack(post, webhook):
    try:
        requests.post(webhook, json={'text': post})
    except RequestException as e:
        message = "An error occurred while attempting to post to slack: "
        message += str(e)
        send_mail(message=message, to=admin_email)
        print('\n terminating the script...')
        raise NetworkError


# functions for emailing lunches

def lunches_dict_to_html(lunches_dict):

    html = "<html><head></head><body>"

    for restaurant in lunches_dict.keys():
        html += "<h3>{0}</h3><p><pre>{1}</pre></p>".format(
            restaurant, lunches_dict[restaurant])

    html += "</body></html>"

    return html


def send_mail(message, to, sender=email_address, password=email_password):

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['Subject'] = "Dzisiejsza oferta lunchowa: {}".format(date_today())

    body = message
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        text = msg.as_string()
        server.sendmail(sender, to, text)
        server.quit()
    except (smtplib.SMTPException, socket.gaierror) as e:
        print('An error occurred trying to send an email: ')
        print(e)
        print('\n terminating the script...')
        raise NetworkError
