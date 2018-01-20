import datetime
import smtplib
import sys

import facebook
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import restaurants, posts_limit, keywords
from credentials import USER_TOKEN, email_address, email_password
from mailing_list import mailing_list


def start_graph(access_token=USER_TOKEN):
    graph = facebook.GraphAPI(access_token=access_token)
    return graph


def _fetch_restaurant_posts(graph, restaurant_id, limit=posts_limit):
    resp = graph.get_object(
        id=restaurant_id,
        fields='posts.limit({})'.format(limit)
    )
    return resp


def _is_about_lunch(post, keywords):
    return any(word in post['message'].split() for word in keywords)


def _date_today():
    now = datetime.datetime.now()
    # return now.strftime("%Y-%m-%d")
    return "2018-01-19"


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

    lunches = {}
    for rest_name, rest_id in restaurants.items():
        resp = _fetch_restaurant_posts(graph, rest_id, limit)
        lunches[rest_name] = _find_todays_lunch_single_restaurant(
            resp, keywords)
    return lunches


def _check_lunches(lunches_dict):
    if not all(lunches_dict.values()):
        return False
    else:
        return True


def send_menu(lunches_dict, mailing_list):
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

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    text = msg.as_string()
    server.sendmail(sender, to, text)
    server.quit()


def exit_script(bool):
    if not bool:
        print("One of the restaurants has not posted about today's lunch yet")
        print("Try again later.")
        sys.exit(1)

if __name__ == '__main__':
    graph = start_graph()
    lunches = find_todays_lunch_all_restaurants(graph)
    b = send_menu(lunches, mailing_list)
    exit_script(b)

#TODO: add unittests
#TODO: docstrings
#TODO: schedule automatic script execution
#TODO: add redoing the script if exit code is 1 every x minutes