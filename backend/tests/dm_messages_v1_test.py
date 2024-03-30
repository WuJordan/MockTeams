import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from tests.helper_for_tests import auth_register_t, dm_create_t, dm_messages_t

@pytest.fixture
def reset_data():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def first_register_id():
    response = auth_register_t(
        "johncitizen@gmail.com", 
        "password",
        "John",
        "Citizen"
    )
    return response.json()

@pytest.fixture
def second_register_id():
    response = auth_register_t(
        "jasminecitizen@gmail.com", 
        "password",
        "Jasmine",
        "Citizen"
    )
    return response.json()

def test_dm_messages_invalid_user_token(reset_data, first_register_id):
    direct_message = dm_create_t(first_register_id['token'], [])
    response = dm_messages_t(first_register_id['token'] + '1', direct_message.json()['dm_id'], 0)
    
    assert response.status_code == AccessError.code

def test_dm_messages_invalid_dm(reset_data, first_register_id):
    response = dm_messages_t(first_register_id['token'], 0, 0)
    assert response.status_code == InputError.code

def test_dm_messages_start_greater_num_messages(reset_data, first_register_id):
    direct_message = dm_create_t(first_register_id['token'], [])
    response = dm_messages_t(first_register_id['token'], direct_message.json()['dm_id'], 5)
    assert response.status_code == InputError.code

def test_dm_messages_valid_dm_non_authorised_user(reset_data, first_register_id, second_register_id):
    direct_message = dm_create_t(first_register_id['token'], [])
    response = dm_messages_t(second_register_id['token'], direct_message.json()['dm_id'], 0)
    assert response.status_code == AccessError.code

def test_dm_messages_no_messages(reset_data, first_register_id, second_register_id):
    direct_message = dm_create_t(first_register_id['token'], [second_register_id['auth_user_id']])
    response = dm_messages_t(second_register_id['token'], direct_message.json()['dm_id'], 0)
    assert response.json() == {'messages': [], 'start': 0, 'end': -1}


