import pytest 
import requests
import json
from src import config
from src.error import AccessError, InputError
from tests.helper_for_tests import auth_register_t, user_profile_t, admin_user_remove_t

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

def test_user_profile_invalid_token(reset_data, register_valid):
    response = user_profile_t(register_valid['token'] + '1', register_valid['auth_user_id'])
    assert response.status_code == AccessError.code

def test_user_profile_invalid_u_id(reset_data, register_valid):
    response = user_profile_t(register_valid['token'], register_valid['auth_user_id'] + 1)
    assert response.status_code == InputError.code 

def test_user_profile_invalid_u_id_invalid_token(reset_data, register_valid):
    response = user_profile_t(register_valid['token'] + '1', register_valid['auth_user_id'] + 1)
    assert response.status_code == AccessError.code

def test_user_profile_one_user(reset_data, register_valid):
    response = user_profile_t(register_valid['token'], register_valid['auth_user_id'])
    assert response.json() == {
        'user': {
            'u_id': register_valid['auth_user_id'],
            'email': 'heart@of.gold',
            'name_first': 'arthur',
            'name_last': 'dent',
            'handle_str': 'arthurdent',
        },
    }

def test_user_profile_user1_calling_user2_id(reset_data, register_valid, register_second):
    response = user_profile_t(register_valid['token'], register_second['auth_user_id'])
    assert response.json() == {
        'user': {
            'u_id': register_second['auth_user_id'],
            'email': 'example@example.com',
            'name_first': 'arthur',
            'name_last': 'dent',
            'handle_str': 'arthurdent0',
        },
    }

def test_user_profile_user1_calling_removed_user(reset_data, register_valid, register_second):
    admin_user_remove_t(register_valid['token'], register_second['auth_user_id'])
    response = user_profile_t(register_valid['token'], register_second['auth_user_id'])

    response_data = response.json()
    assert response_data['user']['u_id'] == register_second['auth_user_id']
    assert response_data['user']['name_first'] == 'Removed'
    assert response_data['user']['name_last'] == 'user'

def test_user_profile_removed_user2_calling_user1(reset_data, register_valid, register_second):
    admin_user_remove_t(register_valid['token'], register_second['auth_user_id'])
    response = user_profile_t(register_second['token'], register_valid['auth_user_id'])
    assert response.status_code == AccessError.code

