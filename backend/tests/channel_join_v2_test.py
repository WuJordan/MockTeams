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


def test_channel_join_invalid_auth_id(reset_data):
    response = requests.post(config.url + 'channel/join/v2', json={
        'token' : '0',
        'channel_id' : 0
        }
    )
    assert response.status_code == AccessError.code

def test_channel_join_invalid_auth_id_valid_channel(reset_data, first_register_id):
    channel = requests.post(CHANNEL_URL, json={
        'token' : first_register_id['token'],
        'name' : 'General',
        'is_public' : True
        }
    )
    response = requests.post(config.url + 'channel/join/v2', json={
        'token' : first_register_id['token'] + '1' ,
        'channel_id' : channel.json()['channel_id']
        }
    )
    assert response.status_code == AccessError.code

def test_channel_join_user_already_member(reset_data, first_register_id):
    channel = requests.post(CHANNEL_URL, json={
        'token' : first_register_id['token'],
        'name' : 'General',
        'is_public' : True
        }
    )
    response = requests.post(config.url + 'channel/join/v2', json={
        'token' : first_register_id['token'],
        'channel_id' : channel.json()['channel_id']
        }
    )
    assert response.status_code == InputError.code

def test_channel_join_user_already_member_private(reset_data, first_register_id):
    channel = requests.post(CHANNEL_URL, json={
        'token' : first_register_id['token'],
        'name' : 'General',
        'is_public' : False
        }
    )
    response = requests.post(config.url + 'channel/join/v2', json={
        'token' : first_register_id['token'],
        'channel_id' : channel.json()['channel_id']
        }
    )
    assert response.status_code == InputError.code

def test_channel_join_valid_channel(reset_data, first_register_id, second_register_id):
    channel_0 = requests.post(CHANNEL_URL, json={
        'token' : first_register_id['token'],
        'name' : 'Channel0',
        'is_public' : True
        }
    )
    requests.post(config.url + 'channel/join/v2', json={
        'token' : second_register_id['token'],
        'channel_id' : channel_0.json()['channel_id']
        }
    )
    details = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : second_register_id['token'],
            "channel_id" : channel_0.json()['channel_id']
            }
        )
    assert details.json()['name'] == "Channel0"
    assert details.json()['is_public'] == True
    assert {
                'u_id': first_register_id['auth_user_id'],
                'email': 'johncitizen@gmail.com',
                'name_first': 'John',
                'name_last': 'Citizen',
                'handle_str': 'johncitizen',
            } in details.json()['owner_members']
    assert {
                'u_id': first_register_id['auth_user_id'],
                'email': 'johncitizen@gmail.com',
                'name_first': 'John',
                'name_last': 'Citizen',
                'handle_str': 'johncitizen',
            } in details.json()['all_members']
    assert {
                'u_id': second_register_id['auth_user_id'],
                'email': 'jasminecitizen@gmail.com',
                'name_first': 'Jasmine',
                'name_last': 'Citizen',
                'handle_str': 'jasminecitizen',
            } in details.json()['all_members']

def test_channel_join_invalid_channel(reset_data, first_register_id):
    response = requests.post(config.url + 'channel/join/v2', json={
        'token' : first_register_id['token'],
        'channel_id' : 0
        }
    )
    assert response.status_code == InputError.code

def test_channel_join_private_not_global_owner(reset_data, first_register_id, second_register_id):
    channel_0 = requests.post(CHANNEL_URL, json={
        'token' : first_register_id['token'],
        'name' : 'Channel0',
        'is_public' : False
        }
    )
    response = requests.post(config.url + 'channel/join/v2', json={
        'token' : second_register_id['token'],
        'channel_id' : channel_0.json()['channel_id']
        }
    )
    assert response.status_code == AccessError.code

def test_channel_join_private_is_global_owner(reset_data, first_register_id, second_register_id):
    channel_0 = requests.post(CHANNEL_URL, json={
        'token' : second_register_id['token'],
        'name' : 'Channel0',
        'is_public' : False
        }
    )
    requests.post(config.url + 'channel/join/v2', json={
        'token' : first_register_id['token'],
        'channel_id' : channel_0.json()['channel_id']
        }
    )
    details = requests.get(config.url + 'channel/details/v2',
        params = {
            "token" : first_register_id['token'],
            "channel_id" : channel_0.json()['channel_id']
            }
        )
    assert details.json()['name'] == "Channel0"
    assert details.json()['is_public'] == False
    assert {
                'u_id': second_register_id['auth_user_id'],
                'email': 'jasminecitizen@gmail.com',
                'name_first': 'Jasmine',
                'name_last': 'Citizen',
                'handle_str': 'jasminecitizen',
            } in details.json()['owner_members']
    assert {
                'u_id': first_register_id['auth_user_id'],
                'email': 'johncitizen@gmail.com',
                'name_first': 'John',
                'name_last': 'Citizen',
                'handle_str': 'johncitizen',
            } in details.json()['all_members']
    assert {
                'u_id': second_register_id['auth_user_id'],
                'email': 'jasminecitizen@gmail.com',
                'name_first': 'Jasmine',
                'name_last': 'Citizen',
                'handle_str': 'jasminecitizen',
            } in details.json()['all_members']
