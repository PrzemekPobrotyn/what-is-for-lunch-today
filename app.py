# very rough sketch of what the app is like?

from flask import Flask
from twilio.twiml.voice_response import VoiceResponse, Say


def order_lunch_twiml(meat_no, vege_no):
    response = VoiceResponse()
    response.say(
        "Dzień dobry, tu S-igmobot. Chciałabym zamówić {} zestawy "
        "mięsne i {} zestaw wegetariański.".format(meat_no, vege_no),
        voice='alice', language='pl-PL')
    # response.say(
    #     'Hello, this is a bot. We would like to order {} meat lunches and'
    #     ' {} vegetarian lunches'.format(meat_no, vege_no), voice='alice',
    #     language='en-GB'
    # )
    return str(response)


app = Flask(__name__)


@app.route('/xml/<int:meat_no><int:vege_no>', methods=['POST'])
def return_twiml(meat_no, vege_no):
    return order_lunch_twiml(meat_no, vege_no)


app.run(use_reloader=True, use_debugger=True, threaded=True)