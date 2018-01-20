from credentials import USER_TOKEN
from config import restaurants, posts_limit, keywords, mailing_list
import facebook
import sys
import datetime

# just playing around
graph = facebook.GraphAPI(access_token=USER_TOKEN)
# resp = graph.request('/search?q=Poetry&type=event&limit=10000')

# fetch posts
resp = graph.get_object(
    id="centrumswiatacom",
    fields='posts.limit({})'.format(posts_limit))
# iterate over posts to find the most recent containing one of the keywords
message = None
for post in resp['posts']['data']:
    try:
        if any(word in post['message'] for word in keywords):
            message = post['message']
            print(post['created_time'])
            print(post['created_time'][:10])
            print(message)
            print('~~~~~~~~~~~~~~~~~~~')
    except KeyError:
        pass

if not message:
    print('No lunch posts yet, redo.')
    sys.exit(1)


def date_today():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")


def start_graph(access_token = USER_TOKEN):
    graph = facebook.GraphAPI(access_token=access_token)
    return graph


def fetch_restaurants_posts(graph, restaurant_name, limit=posts_limit):
    resp = graph.get_object(
        id=restaurant_name,
        fields='posts.limit({})'.format(limit)
    )
    return resp


def is_about_lunch(post, keywords):
    return any(word in post['message'] for word in keywords)


def is_today(post):
    return post['created_time'][:10] == date_today()


def find_todays_lunch(resp, keywords=keywords):
    message = None
    for post in resp['posts']['data']:
        try:
            if is_about_lunch(post, keywords) and is_today(post):
                message = post['message']
        except KeyError:
            pass
    return message

def send_menu(message, mailing_list):


def was_lunch_found(message):
    if message:
