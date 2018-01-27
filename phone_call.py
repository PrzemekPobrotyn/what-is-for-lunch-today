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
