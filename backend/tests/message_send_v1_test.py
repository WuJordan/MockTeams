import pytest
import requests
import json
from src import config
from src.error import AccessError, InputError

REGISTER_URL = config.url + "auth/register/v2"
CHANNEL_URL = config.url + "channels/create/v2"
SEND_URL = config.url + "message/send/v1"
MESSAGES_URL = config.url + "channel/messages/v2"

@pytest.fixture
def reset_data():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def register_valid():
    register = requests.post(REGISTER_URL, json={"email" : "heart@of.gold", "password" : "the_meaning_of_everything_is_42", "name_first" : "arthur", "name_last" : "dent"})
    return register.json()

@pytest.fixture
def register_second():
    register = requests.post(REGISTER_URL, json={"email" : "email@of.gold", "password" : "the_meaning_of_everything_is_42", "name_first" : "arthur", "name_last" : "dent"})
    return register.json()

def test_message_send_invalid_token_invalid_channel(reset_data):
    response = requests.post(
        SEND_URL, 
        json={
            'token': 'bad_token',
            'channel_id': 0,
            'message': "Andrew Taylor says don't ask your tutor or classmates out"
        }
    )
    assert response.status_code == AccessError.code

def test_message_send_invalid_token(reset_data, register_valid):
    channel = requests.post(
        CHANNEL_URL,
        json={
            'token': register_valid['token'],
            'name': 'General',
            'is_public': True
        }
    )
    response = requests.post(
        SEND_URL, 
        json={
            'token': register_valid['token'] + '1',
            'channel_id': channel.json()['channel_id'],
            'message': "Andrew Taylor says don't ask your tutor or classmates out"
        }
    )
    assert response.status_code == AccessError.code

def test_message_send_invalid_channel(reset_data, register_valid):
    response = requests.post(
        SEND_URL, 
        json={
            'token': register_valid['token'],
            'channel_id': 0,
            'message': "Andrew Taylor says don't ask your tutor or classmates out"
        }
    )
    assert response.status_code == InputError.code

def test_message_send_user_not_member_public(reset_data, register_valid, register_second):
    channel = requests.post(
        CHANNEL_URL,
        json={
            'token': register_valid['token'],
            'name': 'General',
            'is_public': True
        }
    )
    response = requests.post(
        SEND_URL,
        json={
            'token': register_second['token'],
            'channel_id': channel.json()['channel_id'],
            'message': "Andrew Taylor says don't ask your tutor or classmates out"
        }
    )
    assert response.status_code == AccessError.code

def test_message_send_user_not_member_private(reset_data, register_valid, register_second):
    channel = requests.post(
        CHANNEL_URL,
        json={
            'token': register_valid['token'],
            'name': 'General',
            'is_public': False
        }
    )
    response = requests.post(
        SEND_URL,
        json={
            'token': register_second['token'],
            'channel_id': channel.json()['channel_id'],
            'message': "Andrew Taylor says don't ask your tutor or classmates out"
        }
    )
    assert response.status_code == AccessError.code

def test_message_send_message_less_than_1_char_public(reset_data, register_valid):
    channel = requests.post(
        CHANNEL_URL,
        json={
            'token': register_valid['token'],
            'name': 'General',
            'is_public': True
        }
    )
    response = requests.post(
        SEND_URL,
        json={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'message': ""
        }
    )
    assert response.status_code == InputError.code

def test_message_send_message_less_than_1_char_private(reset_data, register_valid):
    channel = requests.post(
        CHANNEL_URL,
        json={
            'token': register_valid['token'],
            'name': 'General',
            'is_public': False
        }
    )
    response = requests.post(
        SEND_URL,
        json={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'message': ""
        }
    )
    assert response.status_code == InputError.code

def test_message_send_message_over_1000_char_public(reset_data, register_valid):
    channel = requests.post(
        CHANNEL_URL,
        json={
            'token': register_valid['token'],
            'name': 'General',
            'is_public': True
        }
    )
    response = requests.post(
        SEND_URL,
        json={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'message': "spam" * 250 + '1'
        }
    )
    assert response.status_code == InputError.code

def test_message_send_message_over_1000_char_private(reset_data, register_valid):
    channel = requests.post(
        CHANNEL_URL,
        json={
            'token': register_valid['token'],
            'name': 'General',
            'is_public': False
        }
    )
    response = requests.post(
        SEND_URL,
        json={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'message': "spam" * 250 + '1'
        }
    )
    assert response.status_code == InputError.code

def test_message_send_success_public_channel(reset_data, register_valid):
    channel = requests.post(
        CHANNEL_URL,
        json={
            'token': register_valid['token'],
            'name': 'General',
            'is_public': True
        }
    )
    message = requests.post(
        SEND_URL,
        json={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'message': "Andrew Taylor says don't ask your tutor or classmates out"
        }
    )
    response = requests.get(
        MESSAGES_URL,
        params={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'start': 0
        }
    )
    first_message = response.json()['messages'][0]

    assert first_message['message_id'] == message.json()['message_id']
    assert first_message['u_id'] == register_valid['auth_user_id']
    assert first_message['message'] == "Andrew Taylor says don't ask your tutor or classmates out"
    assert isinstance(first_message['time_sent'], int)

def test_message_send_success_private_channel(reset_data, register_valid):
    channel = requests.post(
        CHANNEL_URL,
        json={
            'token': register_valid['token'],
            'name': 'General',
            'is_public': False
        }
    )
    message = requests.post(
        SEND_URL,
        json={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'message': "Andrew Taylor says don't ask your tutor or classmates out"
        }
    )
    response = requests.get(
        MESSAGES_URL,
        params={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'start': 0
        }
    )
    first_message = response.json()['messages'][0]

    assert first_message['message_id'] == message.json()['message_id']
    assert first_message['u_id'] == register_valid['auth_user_id']
    assert first_message['message'] == "Andrew Taylor says don't ask your tutor or classmates out"
    assert isinstance(first_message['time_sent'], int)
