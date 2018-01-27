# NOTES:

# Nexmo seems complicated
# Check if twilio is capable of synthesisng Polish
# purchase a phone number,
# it seems like you'll have to spin up a simple flask app for twilio, which will
# return a twilo xml with instructions on what to do


from twilio.rest import Client

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = "ACeef64fa61ad2133ed1966de9b50c30bd"
auth_token = "001adba6a3434660c880e2770ae7de85"

client = Client(account_sid, auth_token)

call = client.calls.create(
    to="+48725741259",
    from_="+48717375227",
    url="http://0767990c.ngrok.io/xml/21"
)

# sth along these lines, turn it into a function etc