import datetime
import smtplib
import socket
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import facebook
from requests.exceptions import RequestException

from config import restaurants, posts_limit, keywords
from credentials import USER_TOKEN, email_address, email_password, admin_email
from mailing_list import mailing_list


def start_graph(access_token=USER_TOKEN):
    graph = facebook.GraphAPI(access_token=access_token)
    return graph


def _fetch_restaurant_posts(graph, restaurant_id, limit=posts_limit):

    try:
        resp = graph.get_object(
            id=restaurant_id,
            fields='posts.limit({})'.format(limit))
    except (facebook.GraphAPIError, RequestException) as e:
        message = "An error occurred while attempting to fetch facebook posts: "
        message += str(e)
        _send_mail(message=message, to=admin_email)

        print(message)
        print('\n terminating the script...')
        # even though invalid execution, don't want to get stuck in a loop
        # with invalid access token
        sys.exit(0)

    return resp


def _is_about_lunch(post, keywords):
    return any(word in post['message'].split() for word in keywords)


def _date_today():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")


def _is_today(post):
    return post['created_time'][:10] == _date_today()


def _find_todays_lunch_single_restaurant(resp, keywords=keywords):
    message = None
    for post in resp['posts']['data']:
        try:
            if _is_about_lunch(post, keywords) and _is_today(post):
                message = post['message']
        except KeyError:
            pass
    return message


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
        resp = _fetch_restaurant_posts(graph, rest_id, limit)
        lunches[rest_name] = _find_todays_lunch_single_restaurant(
            resp, keywords)
    return lunches


def _check_lunches(lunches_dict):
    """Checks if every restaurant posted their lunch already."""
    if not all(lunches_dict.values()):
        return False
    else:
        return True


def send_menu(lunches_dict, mailing_list):
    """Sends many to all addresses from the mailing list."""
    if _check_lunches(lunches_dict):
        message = _lunches_dict_to_html(lunches_dict)
        _send_mail(message, to=mailing_list)
        return True
    else:
        return False


def _lunches_dict_to_html(lunches_dict):

    html = "<html><head></head><body>"

    for restaurant in lunches_dict.keys():
        html += "<h3>{0}</h3><p><pre>{1}</pre></p>".format(
            restaurant, lunches_dict[restaurant])

    html += "</body></html>"

    return html


def _send_mail(message, to, sender=email_address, password=email_password):

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['Subject'] = "Dzisiejsza oferta lunchowa: {}".format(_date_today())

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
        sys.exit(0)


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
              'Enjoy your meal!'.format(_date_today()))

if __name__ == '__main__':
    try:
        print('DATE: {}'.format(_date_today()))
        graph = start_graph()
        lunches = find_todays_lunch_all_restaurants(graph)
        b = send_menu(lunches, mailing_list)
        exit_script(b)
    finally:
        print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')


#TODO: add unittests