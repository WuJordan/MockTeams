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
            'email': 'example@example.com', 
            'password': 'password1sp@sswd', 
            'name_first': 'arthur', 
            'name_last': 'dent'
        }
    )
    return response.json()

def test_channel_messages_invalid_user_token(reset_data, register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': register_valid['token'], 
            'name': 'magrathea', 
            'is_public': True
        }
    )
    response = requests.get(
        config.url + 'channel/messages/v2',
        params={
            'token': register_valid['token'] + '1', 
            'channel_id': channel.json()['channel_id'], 
            'start': 0
        }
    )
    assert response.status_code == AccessError.code

def test_channel_messages_invalid_channel(reset_data, register_valid):
    response = requests.get(
        config.url + 'channel/messages/v2',
        params={
            'token': register_valid['token'], 
            'channel_id': 0, 
            'start': 0
        }
    )
    assert response.status_code == InputError.code

def test_channel_messages_start_greater_num_messages(reset_data, register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': register_valid['token'], 
            'name': 'magrathea', 
            'is_public': True
        }
    )
    response = requests.get(
        config.url + 'channel/messages/v2',
        params={
            'token': register_valid['token'], 
            'channel_id': channel.json()['channel_id'], 
            'start': 5
        }
    )
    assert response.status_code == InputError.code

def test_channel_messages_valid_channel_user_not_member(reset_data, register_valid, register_second):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': register_valid['token'], 
            'name': 'magrathea', 
            'is_public': True
        }
    )
    response = requests.get(
        config.url + 'channel/messages/v2',
        params={
            'token': register_second['token'], 
            'channel_id': channel.json()['channel_id'], 
            'start': 0
        }
    )
    assert response.status_code == AccessError.code

def test_channel_messages_success_no_messages(reset_data, register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': register_valid['token'], 
            'name': 'magrathea', 
            'is_public': True
        }
    )
    response = requests.get(
        config.url + 'channel/messages/v2',
        params={
            'token': register_valid['token'], 
            'channel_id': channel.json()['channel_id'], 
            'start': 0
        }
    )
    assert response.json() == {'messages': [], 'start': 0, 'end': -1}
