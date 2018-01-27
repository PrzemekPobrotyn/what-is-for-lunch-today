# What's for lunch?

In this repo we present a script for automatically fetching lunch menus from your favourit restaurants' Facebook pages and delivering them straigh to your Slack channel or mailbox.

We also give a walkthrough on how to set this script up and running on macOS, including scheduling script execution using `launchd`.

### CONFIG
`config` directory contains three files:
* `config.py` - this repo contains config file used by me. Change appropriate variables to suit your needs, details of what each variable means below.
* `credentials.py` - this file should keep your login credentials to Facebook and Slack APIs, as well as email address and password for the account from which the menus will be sent out. `example_credentials.py` provides a template to fill with your own credentials
* `mailing_list.py` - this file keeps the mailing list in form of a tuple of addresses; `example_mailing_list.py` given as a template.

### USAGE

Clone the repo to `lunch_script` folder. We recommend running the script inside a virtualn environment. Set up a new virtual environment using `virtualenv lunch_script` and activate it with `source lunch_script/bin/activate`. When done, you can deactivate virtualenv with `deactivate` command. 

Run `pip install facebook-sdk` inside the virual environment to install python SDK for Facebook. If you wish to run unit tests yourself, make sure you `pip install pytest` in the virtual environment and run the tests by executing `pytest` in `lunch_script` directory.

Before running the script, you need to set up your own config. 

Set up your own Facebook Graph API authentication token. Fill `USER_TOKEN` variable in `config/credentials.py` with it. 
To post to Slack, you need to create a Slack app in your workspace and set it up with incoming webhook integration. Copy the webhook URL to `slack_webhook` variable in `credentials.py`. Fill other fields in `config.py` and `credentials.py` as explained in the templates.

If you want to mail the menus instead of posting them to Slack, unncomment line 76 in `lunch.py` and fill in `mailing_list.py` with addresses of people you want to be notified of lunch menus. Remember to fill email credentials in `credentials.py`. 

The meaning of each variable in `config.py` is as follows:
* restaurants: a dict where keys are names of restaurants (used in emails or Slack posts) and values are their facebook IDs
* weekly menus: this tuple contains a list of names of those restaurants which post their menus weekly, for the entire week ahead (as opposed to posting daily menus)
* posts_limit: this is the limit of posts to fetch from Facebook when attempting to find current day's menu. If all the restaurants post daily, it's safe to keep it low (say, 5). If some restaurants post once a week, make sure the limit is high enough to retrieve a Monday's post on Friday (20-25 should do)
* keywords: list of words to determine if given post is about lunch, presence of one of them is enough to deem post as being about lunch. Update it to suit your own needs. Best to determine appropriate list of words empirically by observing restaurants' posting habits. Note: the script looks for each keyword as a substring of the entire post, so, say, keyword ` lunch` covers all of `#lunch, lunch:)` etc. 
* days_list: this is a list of weekdays (currently in Polish), used to split up weekly menus into days.

With all the configs and credentials set up, simply run `python lunch.py` to find out what's for lunch today.

### LOGIC OF THE SCRIPT

The script works as follows. After fetching `posts_limit` posts for each of the restaurants from Facebook, it iterates over them and checks whether each post is about lunch (using keywords) and whether it is either from the current day or from a restaurant with weekly menus. 

The script returns the first post found which satisfies the above condition. If the post was from a restaurant with weekly postings, it further extracts the menu for just the current day from the weekly menu. Then the menus for all restaurants are posted to Slack or send out to the mailing list.

### SCHEDULING SCRIPTS EXECUTION

Obviously we don't want to be running the script manually every day. In order to automate its execution, we use macOS's `launchd` (*launch daemon*) to schedule running of `lunch.sh` bash script which repatedly executes `lunch.py` script until all lunches have been fetched. It also collects some logs to a text file in `lunch_script` directory. If there is a fatal error (network error/ authentication credentials out of date), the script execution is stopped and description of the error is emailed to the admin. 

To schedule automatic script execution, put `com.przemek.lunchscript.plist` file into one of the locations:
* `/Library/LaunchDaemons` - put your plist scripts in this folder if your job needs to run even when no users are logged in.
* `/Library/LaunchAgents` - put your plist scripts in this folder if the job is only useful when any user is logged in.
* `$HOME/Library/LaunchAgents` - put your plist files in this folder if the job is only useful when specific user is logged in.

If you put `.plist` file in either of the first two locations, it will be run as root. In the last case, it will be run as a specific user.

Remember to update the path to `lunch.sh` script in the `.plist` file. You should give an absolute path.
The path is held in ` <key>ProgramArguments</key>` tag. The other tags in `.plist` file tell the script to execute every Monday to Friday at 11:30am.

To activate automatic script execution, run `launchctl load com.przemek.lunchscript.plist` in the directory where you've put `.plist` file. To deactivate, run `launchctl unload com.przemek.launchsript.plist`.

Feel free to rename the `.plist` file :)




