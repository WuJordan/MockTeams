import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from tests.helper_for_tests import auth_register_t, user_profile_setemail_t, user_profile_t

@pytest.fixture
def reset_data():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def register_valid():
    return auth_register_t("heart@of.gold", "the_meaning_of_everything_is_42", "arthur", "dent").json()

@pytest.fixture
def register_second():
    return auth_register_t("hello@good.bye", "the_meaning_of_everything_is_42", "arthur", "dent").json()

def test_setemail_success(reset_data, register_valid):
    setemail = user_profile_setemail_t(register_valid["token"], "hello@bye.com")
    assert setemail.status_code == 200
    profile = user_profile_t(register_valid["token"], register_valid["auth_user_id"]).json()
    assert profile["user"]["email"] == "hello@bye.com"

def test_setemail_invalid_email(reset_data, register_valid):
    name_email = user_profile_setemail_t(register_valid["token"], "magrathea")
    assert name_email.status_code == InputError.code
    empty_email = user_profile_setemail_t(register_valid["token"], "")
    assert empty_email.status_code == InputError.code
    no_dot_email = user_profile_setemail_t(register_valid["token"], "magrathea@lost")
    assert no_dot_email.status_code == InputError.code
    no_at_email = user_profile_setemail_t(register_valid["token"], "magrathea.lost")
    assert no_at_email.status_code == InputError.code

def test_setemail_email_already_in_use(reset_data, register_valid, register_second):
    setemail2 = user_profile_setemail_t(register_second["token"], "heart@of.gold")
    assert setemail2.status_code == InputError.code

def test_setemail_invalid_token(reset_data, register_valid):
    handle = user_profile_setemail_t(register_valid["token"] + "DEADBEEF", "hello@bye.com")
    assert handle.status_code == AccessError.code