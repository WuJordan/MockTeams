import pytest
import requests
import json
from src import config
from src.error import AccessError
from tests.helper_for_tests import auth_register_t, channels_create_t, channels_list_t


@pytest.fixture
def reset_data():
    requests.delete(config.url + 'clear/v1')


@pytest.fixture
def register_valid():
    response = auth_register_t(
        'heart@of.gold',
        'the_meaning_of_everything_is_42',
        'arthur',
        'dent'
    )
    return response.json()


@pytest.fixture
def register_second():
    response = auth_register_t(
        'example@example.com',
        'password1sp@sswd',
        'arthur',
        'dent'
    )
    return response.json()


def test_list_channels_invalid_token(reset_data, register_valid):
    response = channels_list_t(register_valid['token'] + '1')
    assert response.status_code == AccessError.code


def test_list_channels_empty_list(reset_data, register_valid):
    response = channels_list_t(register_valid['token'])
    assert response.json() == {'channels': []}


def test_channels_list_public_channel(reset_data, register_valid):
    channel = channels_create_t(
        register_valid['token'],
        'General',
        True
    )
    response = channels_list_t(register_valid['token'])
    assert response.json() == {
        'channels': [
            {
                'channel_id': channel.json()['channel_id'],
                'name': 'General',
            }
        ],
    }


def test_channels_list_private_channel(reset_data, register_valid):
    channel = channels_create_t(
        register_valid['token'],
        'General',
        False
    )
    response = channels_list_t(register_valid['token'])
    assert response.json() == {
        'channels': [
            {
                'channel_id': channel.json()['channel_id'],
                'name': 'General',
            }
        ],
    }


def test_channels_list_two_users_separate_channels_public(reset_data, register_valid, register_second):
    channel = channels_create_t(
        register_valid['token'],
        'General',
        True
    )
    channel2 = channels_create_t(
        register_second['token'],
        'General2',
        True
    )
    response = channels_list_t(register_valid['token'])
    response2 = channels_list_t(register_second['token'])
    assert response.json() == {
        'channels': [
            {
                'channel_id': channel.json()['channel_id'],
                'name': 'General',
            }
        ],
    }
    assert response2.json() == {
        'channels': [
            {
                'channel_id': channel2.json()['channel_id'],
                'name': 'General2',
            }
        ],
    }


def test_channels_list_two_users_separate_channels_private(reset_data, register_valid, register_second):
    channel = channels_create_t(
        register_valid['token'],
        'General',
        False
    )
    channel2 = channels_create_t(
        register_second['token'],
        'General2',
        False
    )
    response = channels_list_t(register_valid['token'])
    response2 = channels_list_t(register_second['token'])
    assert response.json() == {
        'channels': [
            {
                'channel_id': channel.json()['channel_id'],
                'name': 'General',
            }
        ],
    }
    assert response2.json() == {
        'channels': [
            {
                'channel_id': channel2.json()['channel_id'],
                'name': 'General2',
            }
        ],
    }


def test_channels_list_two_users_separate_channels_public_and_private(reset_data, register_valid, register_second):
    channel = channels_create_t(
        register_valid['token'],
        'General',
        True
    )
    channel2 = channels_create_t(
        register_second['token'],
        'General2',
        False
    )
    response = channels_list_t(register_valid['token'])
    response2 = channels_list_t(register_second['token'])
    assert response.json() == {
        'channels': [
            {
                'channel_id': channel.json()['channel_id'],
                'name': 'General',
            }
        ],
    }
    assert response2.json() == {
        'channels': [
            {
                'channel_id': channel2.json()['channel_id'],
                'name': 'General2',
            }
        ],
    }


def test_channels_list_two_channels_one_user_public(reset_data, register_valid):
    channel = channels_create_t(
        register_valid['token'],
        'General',
        True
    )
    channel2 = channels_create_t(
        register_valid['token'],
        'General2',
        True
    )
    response = channels_list_t(register_valid['token'])

    assert is_channel_id_in_list(response.json()['channels'], channel.json()['channel_id'])
    assert is_channel_id_in_list(response.json()['channels'], channel2.json()['channel_id'])

    assert is_channel_name_in_list(response.json()['channels'], 'General')
    assert is_channel_name_in_list(response.json()['channels'], 'General2')


def test_channels_list_two_channels_one_user_private(reset_data, register_valid):
    channel = channels_create_t(
        register_valid['token'],
        'General',
        False
    )
    channel2 = channels_create_t(
        register_valid['token'],
        'General2',
        False
    )
    response = channels_list_t(register_valid['token'])

    assert is_channel_id_in_list(response.json()['channels'], channel.json()['channel_id'])
    assert is_channel_id_in_list(response.json()['channels'], channel2.json()['channel_id'])

    assert is_channel_name_in_list(response.json()['channels'], 'General')
    assert is_channel_name_in_list(response.json()['channels'], 'General2')


def test_channels_list_two_channels_one_user_public_and_private(reset_data, register_valid):
    channel = channels_create_t(
        register_valid['token'],
        'General',
        True
    )
    channel2 = channels_create_t(
        register_valid['token'],
        'General2',
        False
    )
    response = channels_list_t(register_valid['token'])

    assert is_channel_id_in_list(response.json()['channels'], channel.json()['channel_id'])
    assert is_channel_id_in_list(response.json()['channels'], channel2.json()['channel_id'])

    assert is_channel_name_in_list(response.json()['channels'], 'General')
    assert is_channel_name_in_list(response.json()['channels'], 'General2')


def is_channel_id_in_list(channels, channel_id):
    channel_id_in_list = False
    for channel in channels:
        if channel['channel_id'] == channel_id:
            channel_id_in_list = True
    return channel_id_in_list


def is_channel_name_in_list(channels, name):
    channel_name_in_list = False
    for channel in channels:
        if channel['name'] == name:
            channel_name_in_list = True
    return channel_name_in_list
