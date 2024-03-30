import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from tests.helper_for_tests import auth_register_t, channels_create_t

@pytest.fixture
def reset_data():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def register_valid():
    response = auth_register_t(
        "heart@of.gold", 
        "the_meaning_of_everything_is_42", 
        "arthur", 
        "dent"
    )
    return response.json()

def test_create_channel_name_less_than_1_char_public(reset_data, register_valid):
    response = channels_create_t(register_valid['token'], '', True)
    assert response.status_code == InputError.code

def test_create_channel_name_less_than_1_char_private(reset_data, register_valid):
    response = channels_create_t(register_valid['token'], '', False)
    assert response.status_code == InputError.code

def test_create_channel_name_more_than_20_char_public(reset_data, register_valid):
    response = channels_create_t(register_valid['token'], 'qwertyuiopasdfghjklzx', True)
    assert response.status_code == InputError.code

def test_create_channel_name_more_than_20_char_private(reset_data, register_valid):
    response = channels_create_t(register_valid['token'], 'qwertyuiopasdfghjklzx', False)
    assert response.status_code == InputError.code

def test_public_channel_return_type_correct(reset_data, register_valid):
    response = channels_create_t(register_valid['token'], 'Humanity', True)
    response_data = response.json()
    assert isinstance(response_data['channel_id'], int)

def test_private_channel_return_type_correct(reset_data, register_valid):
    response = channels_create_t(register_valid['token'], 'Humanity', False)
    response_data = response.json()
    assert isinstance(response_data['channel_id'], int)

def test_create_channel_invalid_token(reset_data, register_valid):
    response = channels_create_t(register_valid['token'] + '1', 'Humanity', True)
    assert response.status_code == AccessError.code
