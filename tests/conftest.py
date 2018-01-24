# this file will contain pytest fixtures
import pytest


@pytest.fixture
def lunch_post():
    p = {
        'created_time': "2018-01-24",
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
