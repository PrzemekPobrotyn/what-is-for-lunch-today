import argparse
from twilio.rest import Client
from config.credentials import (twilio_account_sid,
                                twilio_auth_token,
                                twilio_phone_number)

from config.config import yellow_pages


def parse_args():
    parser = argparse.ArgumentParser(
        description='Make a phone call and order lunches.')

    parser.add_argument(
        'url',
        help='URL of active ngrok connection with number of lunches specified')

    parser.add_argument(
        'to',
        help='Phone number to be called - restaurant\'s phone number.')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    client = Client(twilio_account_sid, twilio_auth_token)
    call = client.calls.create(
        to=yellow_pages[args.to],
        from_=twilio_phone_number,
        url=args.url)


#TODO: add a script to start a Slack poll and collect reponses
#TODO: based on responses, run flask app, tunnel it with ngrok, fetch ngroks url and pass it as argument to this script to make the right call
#TODO: put it all together and update lunch.sh script to run the entire pipeline: fetch lunches, post them to slack, start a poll, collect responses, call the restaurants and make orders