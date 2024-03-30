import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from tests.helper_for_tests import auth_register_t, dm_create_t, dm_list_t

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

def test_dm_list_invalid_token(reset_data, first_register_id):
    response = dm_list_t(first_register_id['token'] + '1')
    assert response.status_code == AccessError.code

def test_dm_list_empty(reset_data, first_register_id):
    response = dm_list_t(first_register_id['token'])
    assert response.json() == {'dms': []}

def test_dm_list_valid_dm(reset_data, first_register_id):
    direct_message = dm_create_t(first_register_id['token'], [])
    response = dm_list_t(first_register_id['token'])
    assert response.json() == {
        'dms' : [
            {
                'dm_id': direct_message.json()['dm_id'],
                'name': 'johncitizen'
            }
        ]    
    }

def test_dm_list_two_dms_one_user(reset_data, first_register_id, second_register_id):
    direct_message0 = dm_create_t(first_register_id['token'], [])
    direct_message1 = dm_create_t(first_register_id['token'], [second_register_id['auth_user_id']])
     
    response = dm_list_t(first_register_id['token'])
    assert response.json() == {
        'dms': [
            {
                'dm_id': direct_message0.json()['dm_id'],
                'name': 'johncitizen',
            },

            {
                'dm_id': direct_message1.json()['dm_id'],
                'name': 'jasminecitizen, johncitizen',
            }
        ]
    }

