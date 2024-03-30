import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from tests.helper_for_tests import auth_register_t, user_profile_sethandle_t, user_profile_t

@pytest.fixture
def reset_data():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def register_valid():
    return auth_register_t("heart@of.gold", "the_meaning_of_everything_is_42", "arthur", "dent").json()

@pytest.fixture
def register_second():
    return auth_register_t("hello@good.bye", "the_meaning_of_everything_is_42", "arthur", "dent").json()

def test_sethandle_success(reset_data, register_valid):
    sethandle = user_profile_sethandle_t(register_valid["token"], "foo")
    assert sethandle.status_code == 200
    profile = user_profile_t(register_valid["token"], register_valid["auth_user_id"]).json()
    assert profile["user"]["handle_str"] == "foo"

def test_sethandle_less_than_3_chars(reset_data, register_valid):
    sethandle = user_profile_sethandle_t(register_valid["token"], "42")
    assert sethandle.status_code == InputError.code

def test_sethandle_more_than_20_chars(reset_data, register_valid):
    sethandle = user_profile_sethandle_t(register_valid["token"], "abcdefghijklmnopqrstuvwxyz")
    assert sethandle.status_code == InputError.code

def test_sethandle_non_alphnumeric_characters(reset_data, register_valid):
    sethandle = user_profile_sethandle_t(register_valid["token"], "%$#@!")
    assert sethandle.status_code == InputError.code

def test_sethandle_handle_already_in_use(reset_data, register_valid, register_second):
    sethandle1 = user_profile_sethandle_t(register_valid["token"], "foobar")
    assert sethandle1.status_code == 200

    sethandle2 = user_profile_sethandle_t(register_second["token"], "foobar")
    assert sethandle2.status_code == InputError.code

def test_sethandle_invalid_token(reset_data, register_valid):
    handle = user_profile_sethandle_t(register_valid["token"] + "DEADBEEF", "foobar")
    assert handle.status_code == AccessError.code