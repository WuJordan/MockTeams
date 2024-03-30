import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from tests.helper_for_tests import auth_register_t, dm_create_t, dm_details_t, dm_leave_t


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

def test_dm_leave_invalid_token(reset_data, first_register_id):
    direct_message = dm_create_t(first_register_id['token'], [])
    response = dm_leave_t(first_register_id['token'] + '1', direct_message.json()['dm_id'])

    assert response.status_code == AccessError.code

def test_dm_leave_invalid_dm(reset_data, first_register_id):
    response = dm_leave_t(first_register_id['token'], 0)
    assert response.status_code == InputError.code

def test_dm_leave_invalid_token_invalid_dm(reset_data):
    response = dm_leave_t('ILovePython', 0)
    assert response.status_code == AccessError.code

def test_dm_leave_success_one_member(reset_data, first_register_id):
    direct_message = dm_create_t(first_register_id['token'], [])
    dm_leave_t(first_register_id['token'], direct_message.json()['dm_id'])
    details = dm_details_t(first_register_id['token'], direct_message.json()['dm_id'])
    
    assert details.status_code == AccessError.code

def test_dm_leave_success_two_members(reset_data, first_register_id, second_register_id):
    direct_message = dm_create_t(first_register_id['token'], [second_register_id['auth_user_id']])
    dm_leave_t(first_register_id['token'], direct_message.json()['dm_id'])
    details0 = dm_details_t(second_register_id['token'], direct_message.json()['dm_id'])
    assert details0.json()['name'] == 'jasminecitizen, johncitizen'
    assert {
        'u_id': second_register_id['auth_user_id'],
        'email': 'jasminecitizen@gmail.com',
        'name_first': 'Jasmine',
        'name_last': 'Citizen',
        'handle_str': 'jasminecitizen',
        } in details0.json()['members'] 
    
    details1 = dm_details_t(first_register_id['token'], direct_message.json()['dm_id'])
    assert details1.status_code == AccessError.code

def test_dm_leave_two_dms_leave_one(reset_data, first_register_id, second_register_id):
    direct_message0 = dm_create_t(first_register_id['token'], [])
    direct_message1 = dm_create_t(first_register_id['token'], [second_register_id['auth_user_id']])
    dm_leave_t(first_register_id['token'], direct_message1.json()['dm_id'])

    response_0 = dm_details_t(first_register_id['token'], direct_message1.json()['dm_id'])
    assert response_0.status_code == AccessError.code

    response_1 = dm_details_t(first_register_id['token'], direct_message0.json()['dm_id'])
    assert response_1.status_code == 200

def test_dm_leave_user_not_member(reset_data, first_register_id, second_register_id):
    direct_message = dm_create_t(first_register_id['token'], [])
    response = dm_leave_t(second_register_id['token'], direct_message.json()['dm_id'])

    assert response.status_code == AccessError.code

def test_dm_leave_non_owner_member_leaves(reset_data, first_register_id, second_register_id):
    direct_message = dm_create_t(first_register_id['token'], [second_register_id['auth_user_id']])
    response = dm_leave_t(second_register_id['token'], direct_message.json()['dm_id'])
    
    assert response.status_code == 200
