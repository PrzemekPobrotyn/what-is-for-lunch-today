### This branch is work in progress

In this branch, we want to extend current functionality. Once lunches are fetched and posted from Slack, we want to:
* post a poll and collect people's responses (their lunch orders)
* start a local Flask app and expose it using ngrok (needed for next step)
* using Twilio API, call chosen restaurants and make orders using text-to-speech synthesisers.

This way, lunch-ordering will be reduced to making a choice in a Slack poll and everything else will be handled automatically, including place the order at a restaurant.
So far, a basic Flask and Twilio setup is completed. 
TODO: 
* Slack poll and response collection
* script to spin Flask app with the right params, expose it using ngrok and pass ngrok's url to the call-making script
* test the whole thing
