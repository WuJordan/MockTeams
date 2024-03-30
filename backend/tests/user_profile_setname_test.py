import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from tests.helper_for_tests import auth_register_t, user_profile_setname_t, user_profile_t

@pytest.fixture
def reset_data():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def register_valid():
    return auth_register_t("heart@of.gold", "the_meaning_of_everything_is_42", "arthur", "dent").json()

@pytest.fixture
def register_second():
    return auth_register_t("hello@good.bye", "the_meaning_of_everything_is_42", "arthur", "dent").json()

def test_setname_success(reset_data, register_valid):
    setname = user_profile_setname_t(register_valid["token"], "foo", "bar")
    assert setname.status_code == 200
    profile = user_profile_t(register_valid["token"], register_valid["auth_user_id"]).json()
    assert profile["user"]["name_first"] == "foo"
    assert profile["user"]["name_last"] == "bar"

def test_setname_first_less_than_1_char(reset_data, register_valid):
    setname = user_profile_setname_t(register_valid["token"], "", "bar")
    assert setname.status_code == InputError.code

def test_setname_last_less_than_1_char(reset_data, register_valid):
    setname = user_profile_setname_t(register_valid["token"], "foo", "")
    assert setname.status_code == InputError.code

def test_setname_first_more_than_50_chars(reset_data, register_valid):
    setname = user_profile_setname_t(register_valid["token"], "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz", "bar")
    assert setname.status_code == InputError.code

def test_setname_last_more_than_50_chars(reset_data, register_valid):
    setname = user_profile_setname_t(register_valid["token"], "foo", "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz")
    assert setname.status_code == InputError.code

def test_setname_non_alphnumeric_characters(reset_data, register_valid):
    setname = user_profile_setname_t(register_valid["token"], "*(&^(", "$$#@")
    assert setname.status_code == 200

def test_setname_invalid_token(reset_data, register_valid):
    handle = user_profile_setname_t(register_valid["token"] + "DEADBEEF", "foo", "bar")
    assert handle.status_code == AccessError.code