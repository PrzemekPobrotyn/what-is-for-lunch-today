from credentials import USER_TOKEN
from config import restaurants, posts_limit, keywords, mailing_list
import facebook
import sys
import datetime


def _date_today():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")


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


def _is_today(post):
    print(post['created_time'][:10])
    print(_date_today())
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
    print(lunches)
    return lunches


def _check_lunches(lunches_dict):
    if not all(lunches_dict.values()):
        return False
    else:
        return True


def send_menu(lunches_dict, mailing_list):
    if _check_lunches(lunches_dict):
        # send out mailing to mailing_list
        return True
    else:
        return False


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