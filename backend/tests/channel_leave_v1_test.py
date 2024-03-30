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
            'email': 'johncitizen@gmail.com',
            'password': 'password',
            'name_first': 'John',
            'name_last': 'Citizen'
        }
    )
    return response.json()

@pytest.fixture
def second_register_valid():
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

def test_channel_leave_invalid_token(reset_data, register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    )
    response = requests.post(
        config.url + 'channel/leave/v1',
        json={
            'token': register_valid['token'] + '1',
            'channel_id': channel.json()['channel_id']
        }
    )
    assert response.status_code == AccessError.code

def test_channel_leave_invalid_token_invalid_channel(reset_data):
    response = requests.post(
        config.url + 'channel/leave/v1',
        json={
            'token': 'bad_token',
            'channel_id': 0
        }
    )
    assert response.status_code == AccessError.code

def test_channel_leave_invalid_channel(reset_data, register_valid):
    response = requests.post(
        config.url + 'channel/leave/v1',
        json={
            'token': register_valid['token'],
            'channel_id': 0
        }
    )
    assert response.status_code == InputError.code

def test_channel_leave_success_public_channel(reset_data, register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    )
    requests.post(
        config.url + 'channel/leave/v1',
        json={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id']
        }
    )
    details = requests.get(
        config.url + 'channel/details/v2',
        params={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id']
        }
    )
    assert details.status_code == AccessError.code

def test_channel_leave_success_private_channel(reset_data, register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': register_valid['token'],
            'name': 'General',
            'is_public': False
        }
    )
    requests.post(
        config.url + 'channel/leave/v1',
        json={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id']
        }
    )
    details = requests.get(
        config.url + 'channel/details/v2',
        params={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id']
        }
    )
    assert details.status_code == AccessError.code

def test_channel_leave_create_two_channels_leave_one(reset_data, register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    )
    channel_2 = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': register_valid['token'], 
            'name': 'General2', 
            'is_public': True
        }
    )
    requests.post(
        config.url + 'channel/leave/v1',
        json={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id']
        }
    )
    response = requests.get(
        config.url + 'channel/details/v2',
        params={
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id']
        }
    )
    assert response.status_code == AccessError.code
    response = requests.get(
        config.url + 'channel/details/v2',
        params={
            'token': register_valid['token'],
            'channel_id': channel_2.json()['channel_id']
        }
    )
    assert response.status_code == 200

def test_channel_leave_user_not_member_public_channel(reset_data, register_valid, second_register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    )
    response = requests.post(
        config.url + 'channel/leave/v1',
        json={
            'token': second_register_valid['token'],
            'channel_id': channel.json()['channel_id']
        }
    )
    assert response.status_code == AccessError.code

def test_channel_leave_user_not_member_private_channel(reset_data, register_valid, second_register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': register_valid['token'], 
            'name': 'General', 
            'is_public': False
        }
    )
    response = requests.post(
        config.url + 'channel/leave/v1',
        json={
            'token': second_register_valid['token'],
            'channel_id': channel.json()['channel_id']
        }
    )
    assert response.status_code == AccessError.code

def test_channel_leave_non_owner_member_leaves(reset_data, register_valid, second_register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    
    )
    requests.post(
        config.url + 'channel/join/v2',
        json={
            'token': second_register_valid['token'],
            'channel_id': channel.json()['channel_id']
        }
    )
    response = requests.post(
        config.url + 'channel/leave/v1',
        json={
            'token': second_register_valid['token'],
            'channel_id': channel.json()['channel_id']
        }
    )
    assert response.status_code == 200
