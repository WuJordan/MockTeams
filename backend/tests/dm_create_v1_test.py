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

def test_create_dm_invalid_token(reset_data, register_valid):
    response = requests.post(
        config.url + 'dm/create/v1',
        json={
            'token': register_valid['token'] + '1',
            'u_ids': []
        }
    )

    assert response.status_code == AccessError.code

def test_create_dm_invalid_u_id(reset_data, register_valid):
    response = requests.post(
        config.url + 'dm/create/v1',
        json={
            'token': register_valid['token'],
            'u_ids': [register_valid['auth_user_id'] + 1]
        }
    )

    assert response.status_code == InputError.code

def test_create_dm_duplicate_u_ids(reset_data, register_valid, register_second):
    response = requests.post(
        config.url + 'dm/create/v1',
        json={
            'token': register_valid['token'],
            'u_ids': [register_second['auth_user_id'], register_second['auth_user_id']]
        }
    )

    assert response.status_code == InputError.code

def test_create_dm_successful_return_one_member(reset_data, register_valid):
    response = requests.post(
        config.url + 'dm/create/v1',
        json={
            'token': register_valid['token'],
            'u_ids': []
        }
    )

    assert isinstance(response.json()['dm_id'], int)

def test_create_dm_successful_return_two_members(reset_data, register_valid, register_second):
    response = requests.post(
        config.url + 'dm/create/v1',
        json={
            'token': register_valid['token'],
            'u_ids': [register_second['auth_user_id']]
        }
    )

    assert isinstance(response.json()['dm_id'], int)
