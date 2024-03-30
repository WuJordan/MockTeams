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
        json = {
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
        json = {
            'email': 'heart@of.gold',
            'password': 'the_meaning_of_everything_is_42',
            'name_first': 'arthur',
            'name_last': 'dent'
        }
    )
    return response.json()

@pytest.fixture
def third_register_valid():
    response = requests.post(
        config.url + 'auth/register/v2',
        json = {
            'email': 'jasminecitizen@gmail.com',
            'password': 'qwerty1',
            'name_first': 'Jasmine',
            'name_last': 'Citizen'
        }
    )
    return response.json()

def test_channel_removeowner_invalid_token(reset_data, register_valid, second_register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json = {
            'token': register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    )

    invalid_token = register_valid['token'] + '1'
    if invalid_token == second_register_valid['token']:
        invalid_token += '1'
    
    response = requests.post(
        config.url + 'channel/removeowner/v1',
        json = {
            'token': invalid_token,
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register_valid['auth_user_id']
        }
    )
    assert response.status_code == AccessError.code

def test_channel_removeowner_invalid_token_invalid_channel(reset_data, second_register_valid):
    response = requests.post(
        config.url + 'channel/removeowner/v1',
        json = {
            'token': second_register_valid['token'] + '1',
            'channel_id': 0,
            'u_id': second_register_valid['auth_user_id']
        }
    )
    assert response.status_code == AccessError.code

def test_channel_removeowner_invalid_channel(reset_data, register_valid, second_register_valid):
    response = requests.post(
        config.url + 'channel/removeowner/v1',
        json = {
            'token': register_valid['token'],
            'channel_id': 0,
            'u_id': second_register_valid['auth_user_id']
        }
    )
    assert response.status_code == InputError.code

def test_channel_removeowner_invalid_u_id(reset_data, register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json = {
            'token': register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    )
    response = requests.post(
        config.url + 'channel/removeowner/v1',
        json = {
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': register_valid['auth_user_id'] + 1
        }
    )
    assert response.status_code == InputError.code

def test_channel_removeowner_u_id_not_member(reset_data, register_valid, second_register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json = {
            'token': register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    )
    response = requests.post(
        config.url + 'channel/removeowner/v1',
        json = {
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register_valid['auth_user_id']
        }
    )
    assert response.status_code == InputError.code

def test_channel_removeowner_u_id_not_owner(reset_data, register_valid, second_register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json = {
            'token': register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    )

    requests.post(
        config.url + 'channel/join/v2', 
        json = {
            'token': second_register_valid['token'], 
            'channel_id': channel.json()['channel_id']
        }
    )

    response = requests.post(
        config.url + 'channel/removeowner/v1',
        json = {
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register_valid['auth_user_id']
        }
    )
    assert response.status_code == InputError.code

def test_channel_removeowner_u_id_only_owner(reset_data, register_valid, second_register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json = {
            'token': second_register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    )
    requests.post(
        config.url + 'channel/join/v2', 
        json = {
            'token': register_valid['token'], 
            'channel_id': channel.json()['channel_id']
        }
    )
    response = requests.post(
        config.url + 'channel/removeowner/v1',
        json = {
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register_valid['auth_user_id']
        }
    )
    assert response.status_code == InputError.code

def test_channel_removeowner_auth_user_not_owner(reset_data, register_valid, second_register_valid, third_register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json = {
            'token': register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    )
    requests.post(
        config.url + 'channel/join/v2',
        json = {
            'token': second_register_valid['token'], 
            'channel_id': channel.json()['channel_id']
        }
    )
    requests.post(
        config.url + 'channel/join/v2', 
        json = {
            'token': third_register_valid['token'], 
            'channel_id': channel.json()['channel_id']
        }
    )
    requests.post(
        config.url + 'channel/addowner/v1',
        json = {
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': third_register_valid['auth_user_id']
        }
    )
    response = requests.post(
        config.url + 'channel/removeowner/v1',
        json = {
            'token': second_register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': third_register_valid['auth_user_id']
        }
    )
    assert response.status_code == AccessError.code

def test_channel_removeowner_auth_user_not_member(reset_data, register_valid, second_register_valid, third_register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json = {
            'token': register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    )
    requests.post(
        config.url + 'channel/join/v2', 
        json = {
            'token': third_register_valid['token'], 
            'channel_id': channel.json()['channel_id']
        }
    )
    requests.post(
        config.url + 'channel/addowner/v1',
        json = {
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': third_register_valid['auth_user_id']
        }
    )
    response = requests.post(
        config.url + 'channel/removeowner/v1',
        json = {
            'token': second_register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': third_register_valid['auth_user_id']
        }
    )
    assert response.status_code == AccessError.code

def test_channel_removeowner_success_auth_channel_owner(reset_data, register_valid, second_register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json = {
            'token': register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    )
    requests.post(
        config.url + 'channel/join/v2',
        json = {
            'token': second_register_valid['token'], 
            'channel_id': channel.json()['channel_id']
        }
    )
    requests.post(
        config.url + 'channel/addowner/v1',
        json = {
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register_valid['auth_user_id']
        }
    )
    requests.post(
        config.url + 'channel/removeowner/v1',
        json = {
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register_valid['auth_user_id']
        }
    )
    details = requests.get(
        config.url + 'channel/details/v2',
        params = {
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id']
        }
    ).json()
    assert {
                'u_id': register_valid['auth_user_id'],
                'email': 'johncitizen@gmail.com',
                'name_first': 'John',
                'name_last': 'Citizen',
                'handle_str': 'johncitizen',
            } in details['owner_members']
    assert {
                'u_id': second_register_valid['auth_user_id'],
                'email': 'heart@of.gold',
                'name_first': 'arthur',
                'name_last': 'dent',
                'handle_str': 'arthurdent',
            } not in details['owner_members']

def test_channel_removeowner_success_auth_global_owner(reset_data, register_valid, second_register_valid, third_register_valid):
    channel = requests.post(
        config.url + 'channels/create/v2', 
        json = {
            'token': second_register_valid['token'], 
            'name': 'General', 
            'is_public': True
        }
    )
    requests.post(
        config.url + 'channel/join/v2',
        json = {
            'token': register_valid['token'], 
            'channel_id': channel.json()['channel_id']
        }
    )
    requests.post(
        config.url + 'channel/join/v2',
        json = {
            'token': third_register_valid['token'], 
            'channel_id': channel.json()['channel_id']
        }
    )
    requests.post(
        config.url + 'channel/addowner/v1',
        json = {
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': third_register_valid['auth_user_id']
        }
    )
    requests.post(
        config.url + 'channel/removeowner/v1',
        json = {
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register_valid['auth_user_id']
        }
    )
    details = requests.get(
        config.url + 'channel/details/v2',
        params = {
            'token': register_valid['token'],
            'channel_id': channel.json()['channel_id']
        }
    ).json()
    assert {
                'u_id': second_register_valid['auth_user_id'],
                'email': 'heart@of.gold',
                'name_first': 'arthur',
                'name_last': 'dent',
                'handle_str': 'arthurdent',
            } not in details['owner_members']
    assert {
                'u_id': third_register_valid['auth_user_id'],
                'email': 'jasminecitizen@gmail.com',
                'name_first': 'Jasmine',
                'name_last': 'Citizen',
                'handle_str': 'jasminecitizen',
            } in details['owner_members']
