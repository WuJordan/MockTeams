import pytest
import requests
import json
from src import config
from src.error import AccessError, InputError
from tests.helper_for_tests import auth_register_t, channels_create_t, dm_create_t
from tests.helper_for_tests import message_remove_t, message_send_t, message_senddm_t
from tests.helper_for_tests import channel_join_t, dm_leave_t, channel_leave_t

@pytest.fixture
def reset_data():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def register_valid():
    register = auth_register_t(
        "heart@of.gold", 
        "the_meaning_of_everything_is_42", 
        "arthur", 
        "dent"
    )
    return register.json()

@pytest.fixture
def register_second():
    register = auth_register_t(
        "email@of.gold", 
        "the_meaning_of_everything_is_42", 
        "arthur", 
        "dent"
    )
    return register.json()

def test_message_remove_invalid_token_invalid_message(reset_data):
    response = message_remove_t("bad_token", 0)
    assert response.status_code == AccessError.code

def test_message_remove_invalid_token_valid_message_in_channel(reset_data, register_valid):
    channel = channels_create_t(register_valid['token'], 'General', True)
    message = message_send_t(
        register_valid['token'], 
        channel.json()['channel_id'], 
        "Andrew Taylor says don't ask your tutor or classmates out"
    )
    response = message_remove_t(
        register_valid['token'] + '1',
        message.json()['message_id']
    )
    assert response.status_code == AccessError.code

def test_message_remove_invalid_token_valid_message_in_dm(reset_data, register_valid):
    direct_message = dm_create_t(register_valid['token'], [])
    message = message_senddm_t(
        register_valid['token'], 
        direct_message.json()['dm_id'], 
        "Andrew Taylor says don't ask your tutor or classmates out"
    )
    response = message_remove_t(
        register_valid['token'] + '1',
        message.json()['message_id']
    )
    assert response.status_code == AccessError.code

def test_message_remove_invalid_message(reset_data, register_valid):
    response = message_remove_t(
        register_valid['token'], 0
    )
    assert response.status_code == InputError.code

def test_remove_message_user_no_longer_in_channel(reset_data, register_valid):
    channel = channels_create_t(register_valid['token'], 'General', True)
    message = message_send_t(
        register_valid['token'], 
        channel.json()['channel_id'], 
        "Andrew Taylor says don't ask your tutor or classmates out"
    )
    channel_leave_t(register_valid['token'], channel.json()['channel_id'])
    response = message_remove_t(
        register_valid['token'],
        message.json()['message_id']
    )
    assert response.status_code == InputError.code

def test_remove_message_user_no_longer_in_dm(reset_data, register_valid):
    direct_message = dm_create_t(register_valid['token'], [])
    message = message_senddm_t(
        register_valid['token'], 
        direct_message.json()['dm_id'], 
        "Andrew Taylor says don't ask your tutor or classmates out"
    )
    dm_leave_t(register_valid['token'], direct_message.json()['dm_id'])
    response = message_remove_t(
        register_valid['token'],
        message.json()['message_id']
    )
    assert response.status_code == InputError.code

# def test_remove_message_user_not_sender_nor_owner_channel(reset_data, register_valid, register_second):
#     channel = channels_create_t(register_valid['token'], 'General', True)
#     message = message_send_t(
#         register_valid['token'], 
#         channel.json()['channel_id'], 
#         "Andrew Taylor says don't ask your tutor or classmates out"
#     )
#     channel_join_t(register_second['token'], channel.json()['channel_id'])
#     response = message_remove_t(
#         register_second['token'],
#         message.json()['message_id']
#     )
#     assert response.status_code == AccessError.code

def test_remove_message_user_not_sender_nor_owner_dm(reset_data, register_valid, register_second):
    direct_message = dm_create_t(
        register_valid['token'], 
        [register_second['auth_user_id']]
    )
    message = message_senddm_t(
        register_valid['token'], 
        direct_message.json()['dm_id'], 
        "Andrew Taylor says don't ask your tutor or classmates out"
    )
    response = message_remove_t(
        register_second['token'],
        message.json()['message_id']
    )
    assert response.status_code == AccessError.code

def test_remove_message_success_channel_owner(reset_data, register_valid, register_second):
    channel = channels_create_t(register_second['token'], 'General', True)
    channel_join_t(register_valid['token'], channel.json()['channel_id'])
    message = message_send_t(
        register_valid['token'], 
        channel.json()['channel_id'], 
        "Andrew Taylor says don't ask your tutor or classmates out"
    )
    response = message_remove_t(
        register_second['token'],
        message.json()['message_id']
    )
    assert response.status_code == 200

def test_remove_message_success_channel_global_owner(reset_data, register_valid, register_second):
    channel = channels_create_t(register_second['token'], 'General', True)
    channel_join_t(register_valid['token'], channel.json()['channel_id'])
    message = message_send_t(
        register_second['token'], 
        channel.json()['channel_id'], 
        "Andrew Taylor says don't ask your tutor or classmates out"
    )
    response = message_remove_t(
        register_valid['token'],
        message.json()['message_id']
    )
    assert response.status_code == 200

def test_remove_message_success_channel_member(reset_data, register_valid, register_second):
    channel = channels_create_t(register_valid['token'], 'General', True)
    channel_join_t(register_second['token'], channel.json()['channel_id'])
    message = message_send_t(
        register_second['token'], 
        channel.json()['channel_id'], 
        "Andrew Taylor says don't ask your tutor or classmates out"
    )
    response = message_remove_t(
        register_second['token'],
        message.json()['message_id']
    )
    assert response.status_code == 200

def test_remove_message_success_dm_owner(reset_data, register_valid, register_second):
    direct_message = dm_create_t(
        register_valid['token'], 
        [register_second['auth_user_id']]
    )
    message = message_senddm_t(
        register_second['token'], 
        direct_message.json()['dm_id'], 
        "Andrew Taylor says don't ask your tutor or classmates out"
    )
    response = message_remove_t(
        register_valid['token'],
        message.json()['message_id']
    )
    assert response.status_code == 200

def test_remove_message_success_dm_member(reset_data, register_valid, register_second):
    direct_message = dm_create_t(
        register_valid['token'], 
        [register_second['auth_user_id']]
    )
    message = message_senddm_t(
        register_second['token'], 
        direct_message.json()['dm_id'], 
        "Andrew Taylor says don't ask your tutor or classmates out"
    )
    response = message_remove_t(
        register_second['token'],
        message.json()['message_id']
    )
    assert response.status_code == 200
