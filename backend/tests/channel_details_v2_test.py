import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError

REGISTER_URL = config.url + "auth/register/v2"
CHANNEL_URL = config.url + "channels/create/v2"

@pytest.fixture
def reset_data():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def first_register_id():
    response = requests.post(REGISTER_URL, json={"email" : 'johncitizen@gmail.com', "password" : 'password', "name_first" : 'John', "name_last" : 'Citizen'})
    return response.json()

@pytest.fixture
def second_register_id():
    response = requests.post(REGISTER_URL, json={"email" : 'jasminecitizen@gmail.com', "password" : 'password', "name_first" : 'Jasmine', "name_last" : 'Citizen'})
    return response.json()

@pytest.fixture
def dup_handle_register_id():
    response = requests.post(REGISTER_URL, json={"email" : 'imposter@gmail.com', "password" : 'password', "name_first" : 'John', "name_last" : 'Citizen'})
    return response.json()

def test_channel_details_valid(reset_data, first_register_id):
    channel = requests.post(CHANNEL_URL, json={
        'token' : first_register_id['token'],
        'name' : 'General',
        'is_public' : True
        }
    )  

    response = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : first_register_id['token'],
            "channel_id" : channel.json()['channel_id']
            }
        )

    assert response.json() == {
        "name": "General",
        "is_public": True,
        "owner_members": [
            {
                'u_id': first_register_id['auth_user_id'],
                'email': 'johncitizen@gmail.com',
                'name_first': 'John',
                'name_last': 'Citizen',
                'handle_str': 'johncitizen',
            }
        ],
        "all_members": [
            {
                'u_id': first_register_id['auth_user_id'],
                'email': 'johncitizen@gmail.com',
                'name_first': 'John',
                'name_last': 'Citizen',
                'handle_str': 'johncitizen',
            }
        ]
    }


def test_channel_details_valid_private(reset_data, first_register_id):
    channel = requests.post(CHANNEL_URL, json={
        'token' : first_register_id['token'],
        'name' : 'General',
        'is_public' : False
        }
    ) 
    response = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : first_register_id['token'],
            "channel_id" : channel.json()['channel_id']
            }
        )
    assert response.status_code == 200


def test_channel_details_invalid_auth_id(reset_data, first_register_id):
    channel = requests.post(CHANNEL_URL, json={
        'token' : first_register_id['token'],
        'name' : 'General',
        'is_public' : True
        }
    )
    response = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : first_register_id['token'] + '1',
            "channel_id" : channel.json()['channel_id']
            }
        )
    assert response.status_code == AccessError.code

def test_channel_details_invalid_channel(reset_data, first_register_id):
    response = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : first_register_id['token'],
            "channel_id" : 0
            }
        )
    assert response.status_code == InputError.code

def test_channel_details_unauthorised_user(reset_data, first_register_id, second_register_id):
    channel = requests.post(CHANNEL_URL, json={
        'token' : first_register_id['token'],
        'name' : 'General',
        'is_public' : True
        }
    )
    response = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : second_register_id['token'],
            "channel_id" : channel.json()['channel_id']
            }
        )
    assert response.status_code == AccessError.code
    

def test_channel_details_2_separate_valid_channels_and_users(reset_data, first_register_id, second_register_id):
    channel_0 = requests.post(CHANNEL_URL, json={
        'token' : first_register_id['token'],
        'name' : 'Channel0',
        'is_public' : True
        }
    )
    channel_1 = requests.post(CHANNEL_URL, json={
        'token' : second_register_id['token'],
        'name' : 'Channel1',
        'is_public' : True
        }
    )
    response_0 = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : first_register_id['token'],
            "channel_id" : channel_0.json()['channel_id']
            }
        )
    assert response_0.status_code == 200
    
    response_1 = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : second_register_id['token'],
            "channel_id" : channel_1.json()['channel_id']
            }
        )
    assert response_1.status_code == 200

def test_channel_details_valid_second_user(reset_data, first_register_id, second_register_id):
    channel_0 = requests.post(CHANNEL_URL, json={
        'token' : second_register_id['token'],
        'name' : 'Channel0',
        'is_public' : True
        }
    )
    response_0 = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : second_register_id['token'],
            "channel_id" : channel_0.json()['channel_id']
            }
        )
    assert response_0.status_code == 200

def test_channel_details_dup_user_handle(reset_data, first_register_id, dup_handle_register_id):
    channel_0 = requests.post(CHANNEL_URL, json={
        'token' : dup_handle_register_id['token'],
        'name' : 'Channel0',
        'is_public' : True
        }
    )
    response_0 = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : dup_handle_register_id['token'],
            "channel_id" : channel_0.json()['channel_id']
            }
        )
    assert response_0.status_code == 200

def test_channel_details_no_valid_channels_or_users(reset_data):
    response = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : '0',
            "channel_id" : 0
            }
        )
    assert response.status_code == AccessError.code

def test_channel_details_2_valid_channels(reset_data, first_register_id):
    channel_0 = requests.post(CHANNEL_URL, json={
        'token' : first_register_id['token'],
        'name' : 'Channel0',
        'is_public' : True
        }
    )
    channel_1 = requests.post(CHANNEL_URL, json={
        'token' : first_register_id['token'],
        'name' : 'Channel1',
        'is_public' : True
        }
    )
    response_0 = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : first_register_id['token'],
            "channel_id" : channel_0.json()['channel_id']
            }
        )
    assert response_0.status_code == 200

    response_1 = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : first_register_id['token'],
            "channel_id" : channel_1.json()['channel_id']
            }
        )
    assert response_1.status_code == 200
    