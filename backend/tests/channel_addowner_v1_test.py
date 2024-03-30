import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from tests.helper_for_tests import auth_register_t, channels_create_t, channel_join_t, channel_addowner_t, channel_details_t

@pytest.fixture
def reset_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def register_valid():
    response = auth_register_t(
        'johncitizen@gmail.com',
        'password',
        'John',
        'Citizen'
    )
    return response.json()

@pytest.fixture
def second_register_valid():
    response = auth_register_t(
        'heart@of.gold',
        'the_meaning_of_everything_is_42',
        'arthur',
        'dent'
    )
    return response.json()

@pytest.fixture
def third_register_valid():
    response = auth_register_t(
        'jasminecitizen@gmail.com',
        'qwerty1',
        'Jasmine',
        'Citizen'
    )
    return response.json()

def test_channel_addowner_invalid_token(reset_data, register_valid, second_register_valid):
    channel = channels_create_t(register_valid['token'], 'General', True)

    invalid_token = register_valid['token'] + '1'
    if invalid_token == second_register_valid['token']:
        invalid_token += '1'
    
    response = channel_addowner_t(
        invalid_token,
        channel.json()['channel_id'],
        second_register_valid['auth_user_id']
    )
    assert response.status_code == AccessError.code

def test_channel_addowner_invalid_token_invalid_channel(reset_data, second_register_valid):
    response = channel_addowner_t(
        second_register_valid['token'] + '1',
        0,
        second_register_valid['auth_user_id']
    )
    assert response.status_code == AccessError.code

def test_channel_addowner_invalid_channel(reset_data, register_valid, second_register_valid):
    response = channel_addowner_t(
        register_valid['token'], 0, second_register_valid['auth_user_id']
    )
    assert response.status_code == InputError.code

def test_channel_addowner_invalid_u_id(reset_data, register_valid):
    channel = channels_create_t(register_valid['token'], 'General', True)
    response = channel_addowner_t(
        register_valid['token'],
        channel.json()['channel_id'],
        register_valid['auth_user_id'] + 1
    )
    assert response.status_code == InputError.code

def test_channel_addowner_u_id_not_member(reset_data, register_valid, second_register_valid):
    channel = channels_create_t(register_valid['token'], 'General', True)
    response = channel_addowner_t(
        register_valid['token'],
        channel.json()['channel_id'],
        second_register_valid['auth_user_id']
    )
    assert response.status_code == InputError.code

def test_channel_addowner_u_id_is_owner(reset_data, register_valid, second_register_valid):
    channel = channels_create_t(register_valid['token'], 'General', True)

    channel_join_t(second_register_valid['token'], channel.json()['channel_id'])
    channel_addowner_t(
        register_valid['token'],
        channel.json()['channel_id'],
        second_register_valid['auth_user_id']
    )
    response = channel_addowner_t(
        register_valid['token'],
        channel.json()['channel_id'],
        second_register_valid['auth_user_id']
    )
    assert response.status_code == InputError.code

def test_channel_addowner_auth_user_not_owner(reset_data, register_valid, second_register_valid, third_register_valid):
    channel = channels_create_t(register_valid['token'], 'General', True)
    channel_join_t(second_register_valid['token'], channel.json()['channel_id'])
    channel_join_t(third_register_valid['token'], channel.json()['channel_id'])
    response = channel_addowner_t(
        second_register_valid['token'],
        channel.json()['channel_id'],
        third_register_valid['auth_user_id']
    )
    assert response.status_code == AccessError.code

def test_channel_addowner_auth_user_not_member(reset_data, register_valid, second_register_valid, third_register_valid):
    channel = channels_create_t(register_valid['token'], 'General', True)
    channel_join_t(third_register_valid['token'], channel.json()['channel_id'])
    response = channel_addowner_t(
        second_register_valid['token'],
        channel.json()['channel_id'],
        third_register_valid['auth_user_id']
    )
    assert response.status_code == AccessError.code

def test_channel_addowner_success_auth_channel_owner(reset_data, register_valid, second_register_valid):
    channel = channels_create_t(register_valid['token'], 'General', True)
    channel_join_t(second_register_valid['token'], channel.json()['channel_id'])
    channel_addowner_t(
        register_valid['token'],
        channel.json()['channel_id'],
        second_register_valid['auth_user_id']
    )
    details = channel_details_t(
        register_valid['token'], 
        channel.json()['channel_id']
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
            } in details['owner_members']


def test_channel_addowner_success_auth_global_owner(reset_data, register_valid, second_register_valid, third_register_valid):
    channel = channels_create_t(second_register_valid['token'], 'General', True)
    channel_join_t(register_valid['token'], channel.json()['channel_id'])
    channel_join_t(third_register_valid['token'], channel.json()['channel_id'])
    channel_addowner_t(
        register_valid['token'],
        channel.json()['channel_id'],
        third_register_valid['auth_user_id']
    )
    details = channel_details_t(
        register_valid['token'], 
        channel.json()['channel_id']
    ).json()
    assert {
                'u_id': second_register_valid['auth_user_id'],
                'email': 'heart@of.gold',
                'name_first': 'arthur',
                'name_last': 'dent',
                'handle_str': 'arthurdent',
            } in details['owner_members']
    assert {
                'u_id': third_register_valid['auth_user_id'],
                'email': 'jasminecitizen@gmail.com',
                'name_first': 'Jasmine',
                'name_last': 'Citizen',
                'handle_str': 'jasminecitizen',
            } in details['owner_members']
