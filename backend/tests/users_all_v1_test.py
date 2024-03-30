import pytest
import requests
import json
from src import config
from src.error import AccessError
from tests.helper_for_tests import auth_register_t, users_all_t, admin_user_remove_t


@pytest.fixture
def reset_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def register_valid():
    response = auth_register_t(
        'heart@of.gold',
        'the_meaning_of_everything_is_42',
        'arthur',
        'dent'
    )
    return response.json()


@pytest.fixture
def register_second():
    response = auth_register_t(
        'example@example.com',
        'password1sp@sswd',
        'arthur',
        'dent'
    )
    return response.json()


@pytest.fixture
def register_third():
    response = auth_register_t(
        'john@gmail.com',
        'hi_there_my_name_is_20',
        'harvey',
        'spector'
    )
    return response.json()


def test_users_all_invalid_token(reset_data, register_valid):
    response = users_all_t(register_valid['token'] + '1')
    assert response.status_code == AccessError.code


def test_users_all_one_user(reset_data, register_valid):
    response = users_all_t(register_valid['token'])
    assert response.json() == {
        'users': [
            {
                'u_id': register_valid['auth_user_id'],
                'email': 'heart@of.gold',
                'name_first': 'arthur',
                'name_last': 'dent',
                'handle_str': 'arthurdent',
            },
        ],
    }


def test_users_all_two_users_user1_calling(reset_data, register_valid, register_second):
    response = users_all_t(register_valid['token'])

    assert is_user_in_list(response.json()['users'], register_valid['auth_user_id'], 'heart@of.gold', 'arthur', 'dent', 'arthurdent')

    assert is_user_in_list(response.json()['users'], register_second['auth_user_id'], 'example@example.com', 'arthur', 'dent', 'arthurdent0')


def test_users_all_two_users_user2_calling(reset_data, register_valid, register_second):
    response = users_all_t(register_second['token'])

    assert is_user_in_list(response.json()['users'], register_valid['auth_user_id'], 'heart@of.gold', 'arthur', 'dent', 'arthurdent')

    assert is_user_in_list(response.json()['users'], register_second['auth_user_id'], 'example@example.com', 'arthur', 'dent', 'arthurdent0')


def test_users_all_three_users(reset_data, register_valid, register_second, register_third):
    response = users_all_t(register_valid['token'])

    assert is_user_in_list(response.json()['users'], register_valid['auth_user_id'], 'heart@of.gold', 'arthur', 'dent', 'arthurdent')

    assert is_user_in_list(response.json()['users'], register_second['auth_user_id'], 'example@example.com', 'arthur', 'dent', 'arthurdent0')

    assert is_user_in_list(response.json()['users'], register_third['auth_user_id'], 'john@gmail.com', 'harvey', 'spector', 'harveyspector')


def test_users_all_two_users_user2_removed(reset_data, register_valid, register_second):
    admin_user_remove_t(register_valid['token'], register_second['auth_user_id'])
    response = users_all_t(register_valid['token'])
    assert response.json() == {
        'users': [
            {
                'u_id': register_valid['auth_user_id'],
                'email': 'heart@of.gold',
                'name_first': 'arthur',
                'name_last': 'dent',
                'handle_str': 'arthurdent',
            },
        ],
    }


def test_users_all_two_users_user2_removed_user2_calling(reset_data, register_valid, register_second):
    admin_user_remove_t(register_valid['token'], register_second['auth_user_id'])
    response = users_all_t(register_second['token'])
    assert response.status_code == AccessError.code


def is_user_in_list(users, u_id, email, name_first, name_last, handle_str):
    user_is_in_list = False
    for user in users:
        if user['u_id'] == u_id and user['name_first'] == name_first and user['name_last'] == name_last and user['handle_str'] == handle_str:
            user_is_in_list = True
    return user_is_in_list
