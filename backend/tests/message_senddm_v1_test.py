import pytest
import requests
import json
from src import config
from src.error import AccessError, InputError
from tests.helper_for_tests import auth_register_t, dm_create_t, dm_messages_t, message_senddm_t

@pytest.fixture
def reset_data():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def register_valid():
    response = auth_register_t(
        "johncitizen@gmail.com", 
        "password",
        "John",
        "Citizen"
    )
    return response.json()

@pytest.fixture
def register_second():
    response = auth_register_t(
        "jasminecitizen@gmail.com", 
        "password",
        "Jasmine",
        "Citizen"
    )
    return response.json()

def test_message_senddm_invalid_token_invalid_dm(reset_data):
    response = message_senddm_t('very_bad_token', 0, "COMP1531 is so cool")
    assert response.status_code == AccessError.code

def test_message_senddm_invalid_token(reset_data, register_valid):
    direct_message = dm_create_t(register_valid['token'], [])
    response = message_senddm_t(register_valid['token'] + '1', direct_message.json()['dm_id'], "COMP1531 is so cool")
    assert response.status_code == AccessError.code

def test_message_senddm_invalid_dm(reset_data, register_valid):
    response = message_senddm_t(register_valid['token'], 0, "COMP1531 is so cool")
    assert response.status_code == InputError.code

def test_message_senddm_user_not_member(reset_data, register_valid, register_second):
    direct_message = dm_create_t(register_valid['token'], [])
    response = message_senddm_t(register_second['token'], direct_message.json()['dm_id'], "COMP1531 is so cool")
    assert response.status_code == AccessError.code

def test_message_senddm_message_less_than_1_char(reset_data, register_valid):
    direct_message = dm_create_t(register_valid['token'], [])
    response = message_senddm_t(register_valid['token'], direct_message.json()['dm_id'], "")
    assert response.status_code == InputError.code

def test_message_senddm_message_over_1000_char(reset_data, register_valid):
    direct_message = dm_create_t(register_valid['token'], [])
    response = message_senddm_t(register_valid['token'], direct_message.json()['dm_id'], "spam" * 250 + '1')
    
    assert response.status_code == InputError.code

def test_message_senddm_success(reset_data, register_valid):
    direct_message = dm_create_t(register_valid['token'], [])
    message = message_senddm_t(register_valid['token'], direct_message.json()['dm_id'], "Why is food so expensive?")
    response = dm_messages_t(register_valid['token'], direct_message.json()['dm_id'], 0)

    first_message = response.json()['messages'][0]

    assert first_message['message_id'] == message.json()['message_id']
    assert first_message['u_id'] == register_valid['auth_user_id']
    assert first_message['message'] == "Why is food so expensive?"
    assert isinstance(first_message['time_sent'], int)

def test_message_senddm_success_two_members(reset_data, register_valid, register_second):
    direct_message = dm_create_t(register_valid['token'], [register_second['auth_user_id']])
    message0 = message_senddm_t(register_valid['token'], direct_message.json()['dm_id'], "Why is food so expensive?")
    message1 = message_senddm_t(register_second['token'], direct_message.json()['dm_id'], "$14.25 for a footlong sub? Absolute scam.")
    

    response = dm_messages_t(register_second['token'], direct_message.json()['dm_id'], 0)
    first_message = response.json()['messages'][1]

    assert first_message['message_id'] == message0.json()['message_id']
    assert first_message['u_id'] == register_valid['auth_user_id']
    assert first_message['message'] == "Why is food so expensive?"
    assert isinstance(first_message['time_sent'], int)

    second_message = response.json()['messages'][0]
    #second message sent will take index 0 in dm['messages'] and first_message will move to index 1.

    assert second_message['message_id'] == message1.json()['message_id']
    assert second_message['u_id'] == register_second['auth_user_id']
    assert second_message['message'] == "$14.25 for a footlong sub? Absolute scam."
    assert isinstance(second_message['time_sent'], int)
 
