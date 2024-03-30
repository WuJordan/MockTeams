import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError

@pytest.fixture
def reset_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def register_valid():
    response = requests.post(
        config.url + 'auth/register/v2',
        json={
            'email': 'heart@of.gold',
            'password': 'the_meaning_of_everything_is_42',
            'name_first': 'arthur',
            'name_last': 'dent'
        }
    )
    return response.json()

@pytest.fixture
def register_second():
    response = requests.post(
        config.url + 'auth/register/v2',
        json={
            'email': 'email@of.gold',
            'password': 'the_meaning_of_everything_is_42',
            'name_first': 'arthur',
            'name_last': 'dent'
        }
    )
    return response.json()

def test_remove_dm_invalid_token_invalid_dm(reset_data):
    response = requests.delete(
        config.url + 'dm/remove/v1',
        json={
            'token': 'bad_token',
            'dm_id': 0
        }
    )
    assert response.status_code == AccessError.code

def test_remove_dm_invalid_token(reset_data, register_valid):
    direct_message = requests.post(
        config.url + 'dm/create/v1',
        json={
            'token': register_valid['token'],
            'u_ids': []
        }
    )
    response = requests.delete(
        config.url + 'dm/remove/v1',
        json={
            'token': register_valid['token'] + '1',
            'dm_id': direct_message.json()['dm_id']
        }
    )
    assert response.status_code == AccessError.code

def test_remove_dm_invalid_dm(reset_data, register_valid):
    response = requests.delete(
        config.url + 'dm/remove/v1',
        json={
            'token': register_valid['token'],
            'dm_id': 0
        }
    )
    assert response.status_code == InputError.code

def test_remove_dm_user_is_member_but_not_creator(reset_data, register_valid, register_second):
    direct_message = requests.post(
        config.url + 'dm/create/v1',
        json={
            'token': register_valid['token'],
            'u_ids': [register_second['auth_user_id']]
        }
    )
    response = requests.delete(
        config.url + 'dm/remove/v1',
        json={
            'token': register_second['token'],
            'dm_id': direct_message.json()['dm_id']
        }
    )
    assert response.status_code == AccessError.code

def test_remove_dm_user_not_member(reset_data, register_valid, register_second):
    direct_message = requests.post(
        config.url + 'dm/create/v1',
        json={
            'token': register_valid['token'],
            'u_ids': []
        }
    )
    response = requests.delete(
        config.url + 'dm/remove/v1',
        json={
            'token': register_second['token'],
            'dm_id': direct_message.json()['dm_id']
        }
    )
    assert response.status_code == AccessError.code

def test_remove_dm_user_is_creator_but_left(reset_data, register_valid):
    direct_message = requests.post(
        config.url + 'dm/create/v1',
        json={
            'token': register_valid['token'],
            'u_ids': []
        }
    )
    requests.post(
        config.url + 'dm/leave/v1',
        json={
            'token': register_valid['token'],
            'dm_id': direct_message.json()['dm_id']
        }
    )
    response = requests.delete(
        config.url + 'dm/remove/v1',
        json={
            'token': register_valid['token'],
            'dm_id': direct_message.json()['dm_id']
        }
    )
    assert response.status_code == AccessError.code

def test_remove_dm_success_one_member(reset_data, register_valid):
    direct_message = requests.post(
        config.url + 'dm/create/v1',
        json={
            'token': register_valid['token'],
            'u_ids': []
        }
    )
    response = requests.delete(
        config.url + 'dm/remove/v1',
        json={
            'token': register_valid['token'],
            'dm_id': direct_message.json()['dm_id']
        }
    )
    assert response.status_code == 200
    response = requests.get(
        config.url + 'dm/details/v1',
        params={
            'token': register_valid['token'],
            'dm_id': direct_message.json()['dm_id']
        }
    )
    assert response.status_code == InputError.code

def test_remove_dm_success_two_members(reset_data, register_valid, register_second):
    direct_message = requests.post(
        config.url + 'dm/create/v1',
        json={
            'token': register_valid['token'],
            'u_ids': [register_second['auth_user_id']]
        }
    )
    response = requests.delete(
        config.url + 'dm/remove/v1',
        json={
            'token': register_valid['token'],
            'dm_id': direct_message.json()['dm_id']
        }
    )
    assert response.status_code == 200
    response = requests.get(
        config.url + 'dm/details/v1',
        params={
            'token': register_valid['token'],
            'dm_id': direct_message.json()['dm_id']
        }
    )
    assert response.status_code == InputError.code
    response = requests.get(
        config.url + 'dm/details/v1',
        params={
            'token': register_second['token'],
            'dm_id': direct_message.json()['dm_id']
        }
    )
    assert response.status_code == InputError.code
