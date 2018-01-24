import mock
import utils
import pytest
from config import keywords
import smtplib
import socket


def test_check_lunches_with_lunch_missing(empty_lunches_dict):
    assert not utils.check_lunches(empty_lunches_dict)


def test_check_lunches_no_lunch_missing(lunches_dict):
    assert utils.check_lunches(lunches_dict)


def test_is_about_lunch(lunch_post):
    assert utils.is_about_lunch(lunch_post, keywords)


def test_is_not_about_lunch(non_lunch_post):
    assert utils.is_about_lunch(non_lunch_post, keywords)


@mock.patch('utils.date_today')
def test_is_today(mock_date, lunch_post):
    mock_date.return_value = "2018-01-04"
    assert utils.is_today(lunch_post)


def test_find_todays_lunch_single_restaurant():
    pass


def test_fetch_restaurants_post():
    pass


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



# THIS IS DEAD WRONG!!!
# @mock.patch('smtplib.SMTP')
# def test_send_mail_with_exceptions_raised(mock_server):
#     mock_server.side_effect = smtplib.SMTPException()
#     with pytest.raises(SystemExit) as cm:
#         with pytest.raises(smtplib.SMTPException):
#             utils.send_mail('message', 'to')
#             assert cm.code == 1
#
#     with pytest.raises(SystemExit) as cm:
#         with pytest.raises(socket.gaierror):
#             utils.send_mail('message', 'to')
#             assert cm.code == 1


# @mock.patch('smtplib.SMTP')
# def test_successfully_send_mail(mock_server):
#     utils.send_mail('message', ['to'], 'email_address', 'pass')
#     # assert mock_server.assert_called_once()
#     # assert mock_quit.assert_called_once()
#     # assert instance.login.assert_called_with('email_address', 'pass')
#     # text = ''
#     # assert instance.sendmail.assert_called_with('email_address', 'to', '')
#     # assert instance.quit.assert_called_once()


