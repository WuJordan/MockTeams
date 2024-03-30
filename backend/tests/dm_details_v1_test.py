import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from tests.helper_for_tests import auth_register_t, dm_create_t, dm_details_t

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

@pytest.fixture
def dup_handle_register_id():
    response = auth_register_t(
        "imposter@gmail.com", 
        "password",
        "John",
        "Citizen"
    )
    return response.json()

def test_dm_details_valid(reset_data, first_register_id):
    direct_message = dm_create_t(first_register_id['token'], [])
    response = dm_details_t(first_register_id['token'], direct_message.json()['dm_id'])
    
    assert response.json() == {
        'name': 'johncitizen',
        'members':[
            {
                'u_id': first_register_id['auth_user_id'],
                'email': 'johncitizen@gmail.com',
                'name_first': 'John',
                'name_last': 'Citizen',
                'handle_str': 'johncitizen',
            }
        ],
    }

def test_dm_details_invalid_token(reset_data, first_register_id):
    direct_message = dm_create_t(first_register_id['token'], [])
    response = dm_details_t(first_register_id['token'] + '1', direct_message.json()['dm_id'])
    
    assert response.status_code == AccessError.code

def test_dm_details_invalid_dm(reset_data, first_register_id):
    response = dm_details_t(first_register_id['token'], 0)
    
    assert response.status_code == InputError.code

def test_dm_details_unauthorised_user(reset_data, first_register_id, second_register_id):
    direct_message = dm_create_t(first_register_id['token'], [])
    response = dm_details_t(second_register_id['token'], direct_message.json()['dm_id'])
    
    assert response.status_code == AccessError.code

def test_dm_details_two_authorised_users(reset_data, first_register_id, second_register_id):
    direct_message = dm_create_t(first_register_id['token'], [second_register_id['auth_user_id']])
    response_0 = dm_details_t(second_register_id['token'], direct_message.json()['dm_id'])
    
    assert response_0.json()['name'] == 'jasminecitizen, johncitizen'
    
    assert {
        'u_id': first_register_id['auth_user_id'],
        'email': 'johncitizen@gmail.com',
        'name_first': 'John',
        'name_last': 'Citizen',
        'handle_str': 'johncitizen',
        } in response_0.json()['members']

    assert {
        'u_id': second_register_id['auth_user_id'],
        'email': 'jasminecitizen@gmail.com',
        'name_first': 'Jasmine',
        'name_last': 'Citizen',
        'handle_str': 'jasminecitizen',
        } in response_0.json()['members']
 
    
    response_1 = dm_details_t(first_register_id['token'], direct_message.json()['dm_id'])
    assert response_1.status_code == 200

def test_dm_details_dup_user_handle(reset_data, first_register_id, dup_handle_register_id):
    direct_message = dm_create_t(first_register_id['token'], [dup_handle_register_id['auth_user_id']])
    response = dm_details_t(first_register_id['token'], direct_message.json()['dm_id'])
    
    assert response.json()['name'] == 'johncitizen, johncitizen0'
    assert {
        'u_id': first_register_id['auth_user_id'],
        'email': 'johncitizen@gmail.com',
        'name_first': 'John',
        'name_last': 'Citizen',
        'handle_str': 'johncitizen',
        } in response.json()['members']

    assert {
        'u_id': dup_handle_register_id['auth_user_id'],
        'email': 'imposter@gmail.com',
        'name_first': 'John',
        'name_last': 'Citizen',
        'handle_str': 'johncitizen0',
        } in response.json()['members']

def test_dm_details_no_valid_dm_or_users(reset_data):
    response = dm_details_t('0', 0)
    assert response.status_code == AccessError.code
