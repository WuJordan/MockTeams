import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError

REGISTER_URL = config.url + "auth/register/v2"
CHANNEL_URL = config.url + "channels/create/v2"
INVITE_URL = config.url + "channel/invite/v2"
DETAILS_URL = config.url + "channel/details/v2"
JOIN_URL = config.url + "channel/join/v2"

@pytest.fixture
def reset_data():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def first_register():
    response = requests.post(
        REGISTER_URL, 
        json={
            "email" : 'johncitizen@gmail.com', 
            "password" : 'password', 
            "name_first" : 'John', 
            "name_last" : 'Citizen'
        }
    )
    return response.json()

@pytest.fixture
def second_register():
    response = requests.post(
        REGISTER_URL, 
        json={
            "email" : 'jasminecitizen@gmail.com', 
            "password" : 'password', 
            "name_first" : 'Jasmine', 
            "name_last" : 'Citizen'
        }
    )
    return response.json()

@pytest.fixture
def third_register():
    response = requests.post(
        REGISTER_URL, 
        json={
            "email" : 'heart@of.gold', 
            "password" : 'the_meaning_of_everything_is_42', 
            "name_first" : 'arthur', 
            "name_last" : 'dent'
        }
    )
    return response.json()

def test_channel_invite_success_public_channel(reset_data, first_register, second_register):
    channel = requests.post(
        CHANNEL_URL, 
        json={
            'token' : first_register['token'],
            'name' : 'General',
            'is_public' : True
        }
    )
    response = requests.post(
        INVITE_URL, 
        json={
            'token': first_register['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register['auth_user_id']
        }
    )
    assert response.status_code == 200
    details = requests.get(
        DETAILS_URL, 
        params={
            'token': second_register['token'],
            'channel_id': channel.json()['channel_id']
        }
    ).json()
    assert {
                'u_id': first_register['auth_user_id'],
                'email': 'johncitizen@gmail.com',
                'name_first': 'John',
                'name_last': 'Citizen',
                'handle_str': 'johncitizen',
            } in details['owner_members']
    assert {
                'u_id': first_register['auth_user_id'],
                'email': 'johncitizen@gmail.com',
                'name_first': 'John',
                'name_last': 'Citizen',
                'handle_str': 'johncitizen',
            } in details['all_members']
    assert {
                'u_id': second_register['auth_user_id'],
                'email': 'jasminecitizen@gmail.com',
                'name_first': 'Jasmine',
                'name_last': 'Citizen',
                'handle_str': 'jasminecitizen',
            } in details['all_members']

def test_channel_invite_success_private_channel(reset_data, first_register, second_register):
    channel = requests.post(
        CHANNEL_URL, 
        json={
            'token' : first_register['token'],
            'name' : 'General',
            'is_public' : False
        }
    )
    response = requests.post(
        INVITE_URL, 
        json={
            'token': first_register['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register['auth_user_id']
        }
    )
    assert response.status_code == 200
    details = requests.get(
        DETAILS_URL, 
        params={
            'token': second_register['token'],
            'channel_id': channel.json()['channel_id']
        }
    ).json()
    assert {
                'u_id': first_register['auth_user_id'],
                'email': 'johncitizen@gmail.com',
                'name_first': 'John',
                'name_last': 'Citizen',
                'handle_str': 'johncitizen',
            } in details['owner_members']
    assert {
                'u_id': first_register['auth_user_id'],
                'email': 'johncitizen@gmail.com',
                'name_first': 'John',
                'name_last': 'Citizen',
                'handle_str': 'johncitizen',
            } in details['all_members']
    assert {
                'u_id': second_register['auth_user_id'],
                'email': 'jasminecitizen@gmail.com',
                'name_first': 'Jasmine',
                'name_last': 'Citizen',
                'handle_str': 'jasminecitizen',
            } in details['all_members']

def test_channel_invite_invalid_token(reset_data, first_register, second_register):
    channel = requests.post(
        CHANNEL_URL, 
        json={
            'token' : first_register['token'],
            'name' : 'General',
            'is_public' : True
        }
    )
    invalid_token = first_register['token'] + '1'
    if invalid_token == second_register['token']:
        invalid_token += '1'
    
    response = requests.post(
        INVITE_URL, 
        json={
            'token': invalid_token,
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register['auth_user_id']
        }
    )
    assert response.status_code == AccessError.code

def test_channel_invite_channel_id_invalid(reset_data, first_register, second_register):
    response = requests.post(
        INVITE_URL, 
        json={
            'token': first_register['token'],
            'channel_id': 0,
            'u_id': second_register['auth_user_id']
        }
    )
    assert response.status_code == InputError.code

def test_channel_invite_u_id_invalid(reset_data, first_register):
    channel = requests.post(
        CHANNEL_URL, 
        json={
            'token' : first_register['token'],
            'name' : 'General',
            'is_public' : True
        }
    )
    response = requests.post(
        INVITE_URL, 
        json={
            'token': first_register['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': first_register['auth_user_id'] + 1
        }
    )
    assert response.status_code == InputError.code

def test_channel_invite_u_id_already_member(reset_data, first_register, second_register):
    channel = requests.post(
        CHANNEL_URL, 
        json={
            'token' : first_register['token'],
            'name' : 'General',
            'is_public' : True
        }
    )
    requests.post(
        JOIN_URL, 
        json={
            'token' : second_register['token'],
            'channel_id' : channel.json()['channel_id']
        }
    )
    response = requests.post(
        INVITE_URL, 
        json={
            'token': first_register['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register['auth_user_id']
        }
    )
    assert response.status_code == InputError.code

def test_channel_invite_double_invite_u_id(reset_data, first_register, second_register):
    channel = requests.post(
        CHANNEL_URL, 
        json={
            'token' : first_register['token'],
            'name' : 'General',
            'is_public' : True
        }
    )
    requests.post(
        INVITE_URL, 
        json={
            'token': first_register['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register['auth_user_id']
        }
    )
    response = requests.post(
        INVITE_URL, 
        json={
            'token': first_register['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register['auth_user_id']
        }
    )
    assert response.status_code == InputError.code

def test_channel_invite_valid_channel_auth_user_not_member(reset_data, first_register, second_register, third_register):
    channel = requests.post(
        CHANNEL_URL, 
        json={
            'token' : first_register['token'],
            'name' : 'General',
            'is_public' : True
        }
    )
    response = requests.post(
        INVITE_URL, 
        json={
            'token': third_register['token'],
            'channel_id': channel.json()['channel_id'],
            'u_id': second_register['auth_user_id']
        }
    )
    assert response.status_code == AccessError.code
