import mock
import utils
import pytest
from config import keywords
import smtplib
import facebook
import socket
from requests.exceptions import RequestException
from config.credentials import admin_email
import datetime


# fixtures

@pytest.fixture
def lunch_post():
    p = {
        'created_time': "2018-01-01",
        'message': '#LUNCH rosół i schabowy'
    }
    return p


@pytest.fixture
def non_lunch_post():
    p = {'message': 'This is not about lunch.'}
    return p


@pytest.fixture
def lunches_dict():
    p = {'rest_A': 'pork',
         'rest_B': 'beef'}
    return p


@pytest.fixture()
def empty_lunches_dict():
    return {'rest': None}


@pytest.fixture()
def menu_for_week():
    return 'PONIEDZIAŁEK\nzupa\nWTOREK\nkotlet\nŚRODA\nryż'


@pytest.fixture()
def response():
    resp = {'posts': {
        'data': [
            {'message': 'PONIEDZIAŁEK lunch'},
            {'message': 'WTOREK lunch'}
                ]
                    }
    }
    return resp


@pytest.fixture()
def response_no_message():
    resp = {'posts': {
        'data': [{'key': 'value'}]
                    }
    }
    return resp


# tests

def test_check_lunches_with_lunch_missing(empty_lunches_dict):
    assert not utils.check_lunches(empty_lunches_dict)


def test_check_lunches_no_lunch_missing(lunches_dict):
    assert utils.check_lunches(lunches_dict)


def test_is_about_lunch(lunch_post):
    assert utils.is_about_lunch(lunch_post, keywords)


def test_is_not_about_lunch(non_lunch_post):
    assert utils.is_about_lunch(non_lunch_post, keywords)


@mock.patch('utils.utils.date_today')
def test_is_today(mock_date, lunch_post):
    mock_date.return_value = "2018-01-01"
    assert utils.is_today(lunch_post)


@mock.patch('utils.utils.is_about_lunch')
@mock.patch('utils.utils.is_today')
def test_find_todays_lunch_single_restaurant(
        mock_is_today, mock_is_about_lunch, response):
    mock_is_today.return_value = True
    mock_is_about_lunch.return_value = True
    assert (utils.find_todays_lunch_single_restaurant('Boska', response) ==
            'PONIEDZIAŁEK lunch')


@mock.patch('utils.utils.single_day_from_week_menu')
@mock.patch('utils.utils.is_about_lunch')
@mock.patch('utils.utils.is_today')
def test_find_todays_lunch_single_restaurant_weekly_menu(
        mock_is_today, mock_is_about_lunch, mock_single_day, response):
    mock_is_today.return_value = True
    mock_is_about_lunch.return_value = True
    mock_single_day.return_value = 'PONIEDZIAŁEK lunch'
    assert (utils.find_todays_lunch_single_restaurant('Centrum', response) ==
            'PONIEDZIAŁEK lunch')
    weekday = datetime.datetime.now().weekday()
    mock_single_day.assert_called_once_with('PONIEDZIAŁEK lunch', weekday)


@mock.patch('utils.utils.is_about_lunch')
@mock.patch('utils.utils.is_today')
def test_find_todays_lunch_single_restaurant_no_lunch(
        mock_is_today, mock_is_about_lunch, response):
    mock_is_today.return_value = False

    assert utils.find_todays_lunch_single_restaurant('Boska', response) is None


@mock.patch('utils.utils.is_about_lunch')
@mock.patch('utils.utils.is_today')
def test_find_todays_lunch_single_restaurant_key_error(
        mock_is_today, mock_is_about_lunch, response_no_message):
    mock_is_today.return_value = True
    mock_is_about_lunch.return_value = True
    assert (utils.find_todays_lunch_single_restaurant(
        'Boska', response_no_message) is None)


@mock.patch('utils.utils.send_mail')
def test_fetch_restaurants_post_api_error(mock_send_mail):
    mock_graph = mock.MagicMock(facebook.GraphAPI)
    mock_graph.get_object.side_effect = facebook.GraphAPIError('error')
    with pytest.raises(utils.NetworkError):
        utils.fetch_restaurant_posts(mock_graph, 'restaurant')
        mock_send_mail.assert_called_once_with(
            'An error occurred while attempting to fetch facebook posts: error',
            admin_email)

    mock_graph.get_object.side_effect = RequestException
    with pytest.raises(utils.NetworkError):
        utils.fetch_restaurant_posts(mock_graph, 'restaurant')
        mock_send_mail.assert_called_once(
            'An error occurred while attempting to fetch facebook posts: error',
            admin_email)


def test_successfully_fetch_restaurant_posts():
    mock_graph = mock.MagicMock(facebook.GraphAPI)
    mock_graph.get_object.return_value = 'response'
    assert utils.fetch_restaurant_posts(mock_graph, 'id') == 'response'


def test_single_day_from_week_menu(menu_for_week):
    assert (utils.single_day_from_week_menu(menu_for_week, 0) ==
            'PONIEDZIAŁEK\nzupa')
    assert utils.single_day_from_week_menu(menu_for_week, 3) == ''


def test_lunches_dict_to_slack_post(lunches_dict):
    expected_message = '*REST_A*\n\npork\n\n\n*REST_B*\n\nbeef\n\n\n'
    assert utils.lunches_dict_to_slack_post(lunches_dict) == expected_message


def test_lunches_dict_to_html(lunches_dict):
    expected_html = \
        '<html><head></head><body><h3>rest_A</h3><p><pre>pork</pre></p><h3>' \
        'rest_B</h3><p><pre>beef</pre></p></body></html>'
    assert utils.lunches_dict_to_html(lunches_dict) == expected_html


@mock.patch('utils.utils.send_mail')
@mock.patch('requests.post')
def test_post_to_slack_with_error(mock_post, mock_send_mail):
    mock_post.side_effect = RequestException
    with pytest.raises(utils.NetworkError):
        utils.post_to_slack(mock_post, 'webhook')
        mock_send_mail.assert_called_once(
            'An error occurred while attempting to to post to slack',
            admin_email)


@mock.patch('utils.utils.smtplib.SMTP')
def test_send_mail_with_exceptions_raised(mock_server):
    mock_server.side_effect = smtplib.SMTPException
    with pytest.raises(utils.NetworkError):
        utils.send_mail('message','to',)

    mock_server.side_effect = socket.gaierror
    with pytest.raises(utils.NetworkError):
        utils.send_mail('message', 'to', )


@mock.patch('utils.utils.smtplib.SMTP')
def test_successfully_send_mail(mock_server):
    utils.send_mail('message', ['to'], 'email_address', 'pass')
    mock_server.assert_called_once_with('smtp.gmail.com', 587)
    mock_server.return_value.starttls.assert_called_once()
    mock_server.return_value.login.assert_called_once_with(
        'email_address', 'pass')
    mock_server.return_value.sendmail.assert_called_once()
    mock_server.return_value.quit.assert_called_once()


