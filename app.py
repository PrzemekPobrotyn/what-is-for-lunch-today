from flask import Flask
from twilio.twiml.voice_response import VoiceResponse, Say


def correct_grammar(number):
    """
    Return the correct grammatical form of a word 'zestaw', depending on
    the number in front.
    """
    if number == 1:
        return 'zestaw'
    elif number in [2, 3, 4]:
        return 'zestawy'
    # this isn't quite right, but we won't order enough meals to break the rule
    # eg for 22 it should be 'zestawy', not 'zestawów'.
    elif number > 4:
        return 'zestawów'


def order_lunch_twiml(meat_no, vege_no):
    response = VoiceResponse()

    if meat_no > 0 and vege_no > 0:
        response.say(
            "Dzień dobry, tu S-igmobot. Chciałabym zamówić {} ".format(meat_no) +
            correct_grammar(meat_no) + "mięsne i {} ".format(vege_no) +
            correct_grammar(vege_no) + "wegetariańske do odbioru osobistego. "
            "Dziękuję i do usłyszenia.",
            voice='alice', language='pl-PL')

    elif meat_no == 0:
        response.say(
            "Dzień dobry, tu S igmobot. Chciałabym zamówić {} ".format(vege_no) +
            correct_grammar(vege_no) +
            "wegetariańske do odbioru osobistego. "
            "Dziękuję i do usłyszenia.",
            voice='alice', language='pl-PL')

    elif vege_no == 0:
        response.say(
            "Dzień dobry, tu S-igmobot. Chciałabym zamówić {} ".format(meat_no) +
            correct_grammar(meat_no) +
            "mięsne do odbioru osobistego. "
            "Dziękuję i do usłyszenia.",
            voice='alice', language='pl-PL')

    return str(response)


# spin up the flask app
app = Flask(__name__)


@app.route('/xml/<int:meat_no><int:vege_no>', methods=['POST'])
def return_twiml(meat_no, vege_no):
    return order_lunch_twiml(meat_no, vege_no)


app.run(use_reloader=True, use_debugger=True, threaded=True)

#TODO: change order_lunch_twiml to correctly handle grammar depenind on the number of lunches ordered
#TODO: add route for StatusCallback, handle busy or unanswered calls