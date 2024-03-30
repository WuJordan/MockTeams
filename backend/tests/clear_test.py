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

def test_clear_users_registered(reset_data, register_valid):
    requests.delete(config.url + 'clear/v1')
    response = requests.post(
        config.url + 'auth/login/v2',
        json={
            'email': 'heart@of.gold', 
            'password': 'the_meaning_of_everything_is_42'
        }
    )
    assert response.status_code == InputError.code

def test_clear_public_channel_created(reset_data, register_valid):
    token = register_valid['token']
    response = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': token, 
            'name': 'Humanity', 
            'is_public': True
        }
    )
    requests.delete(config.url + 'clear/v1')
    response = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': token, 
            'name': 'Humanity', 
            'is_public': True
        }
    )
    assert response.status_code == AccessError.code

def test_clear_private_channel_created(reset_data, register_valid):
    token = register_valid['token']
    response = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': token, 
            'name': 'Humanity', 
            'is_public': False
        }
    )
    requests.delete(config.url + 'clear/v1')
    response = requests.post(
        config.url + 'channels/create/v2', 
        json={
            'token': token, 
            'name': 'Humanity', 
            'is_public': False
        }
    )
    assert response.status_code == AccessError.code

def test_clear_dm_created(reset_data, register_valid):
    token = register_valid['token']
    response = requests.post(
        config.url + 'dm/create/v1', 
        json={
            'token': token, 
            'u_ids': []
        }
    )
    requests.delete(config.url + 'clear/v1')
    response = requests.post(
        config.url + 'dm/create/v1', 
        json={
            'token': token, 
            'u_ids': []
        }
    )
    assert response.status_code == AccessError.code
