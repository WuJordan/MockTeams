import pytest
import requests
from src import config
from src.error import InputError, AccessError
from tests.helper_for_tests import auth_login_t, auth_register_t, auth_logout_t

@pytest.fixture
def reset_data():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def register_valid():
    return auth_register_t("heart@of.gold", "the_meaning_of_everything_is_42", "arthur", "dent").json()

def test_register_valid(reset_data, register_valid):
    assert "token" in register_valid
    assert "auth_user_id" in register_valid

def test_register_invalid_email(reset_data):
    name_email = auth_register_t("magrathea", "the_meaning_of_everything_is_42", "arthur", "dent")
    assert name_email.status_code == InputError.code
    empty_email = auth_register_t("", "the_meaning_of_everything_is_42", "arthur", "dent")
    assert empty_email.status_code == InputError.code
    no_dot_email = auth_register_t("magrathea@lost", "the_meaning_of_everything_is_42", "arthur", "dent")
    assert no_dot_email.status_code == InputError.code
    no_at_email = auth_register_t("magrathea.lost", "the_meaning_of_everything_is_42", "arthur", "dent")
    assert no_at_email.status_code == InputError.code

def test_register_duplicate_email(reset_data, register_valid):
    duplicate = auth_register_t("heart@of.gold", "the_meaning_of_everything_is_42", "ford", "prefect")
    assert duplicate.status_code == InputError.code

def test_register_password_6_char_exactly(reset_data):
    pass_6_char = auth_register_t("heart@of.gold", "123456", "ford", "prefect")
    assert pass_6_char.status_code == 200

def test_register_password_less_than_6_char(reset_data):
    small_pass = auth_register_t("heart@of.gold", "42", "ford", "prefect")
    empty_pass = auth_register_t("heart@of.gold", "", "ford", "prefect")

    assert small_pass.status_code == InputError.code
    assert empty_pass.status_code == InputError.code

def test_register_name_first_not_within_1_and_50_chars_incl(reset_data):
    empty_name = auth_register_t("heart@of.gold", "the_meaning_of_everything_is_42", "", "prefect")
    long_name = auth_register_t("heart@of.gold", "the_meaning_of_everything_is_42", "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz", "prefect")

    assert empty_name.status_code == InputError.code
    assert long_name.status_code == InputError.code

def test_register_name_last_not_within_1_and_50_chars_incl(reset_data):
    empty_name = auth_register_t("heart@of.gold", "the_meaning_of_everything_is_42", "ford", "")
    long_name = auth_register_t("heart@of.gold", "the_meaning_of_everything_is_42", "ford", "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz")

    assert empty_name.status_code == InputError.code
    assert long_name.status_code == InputError.code

def test_register_duplicate_name(reset_data, register_valid):
    duplicate = auth_register_t("magrathea@is.lost", "the_meaning_of_everything_is_42", "arthur", "dent")
    assert duplicate.status_code == 200
    register_dupe = duplicate.json()
    assert register_valid["token"] != register_dupe["token"]
    assert register_valid["auth_user_id"] != register_dupe["auth_user_id"]

###############################################################################

def test_register_and_login_success(reset_data, register_valid):
    login = auth_login_t("heart@of.gold", "the_meaning_of_everything_is_42")
    login_response = login.json()

    assert login_response["auth_user_id"] == register_valid["auth_user_id"]
    assert login_response["token"] != register_valid["token"]

def test_login_invalid_email(reset_data):
    symbols_out_of_order = auth_login_t("heart@of.gold", "the_meaning_of_everything_is_42")
    assert symbols_out_of_order.status_code == InputError.code
    name_email = auth_login_t("magrathea", "the_meaning_of_everything_is_42")
    assert name_email.status_code == InputError.code
    empty_email = auth_login_t("", "the_meaning_of_everything_is_42")
    assert empty_email.status_code == InputError.code
    no_dot_email = auth_login_t("magrathea@lost", "the_meaning_of_everything_is_42")
    assert no_dot_email.status_code == InputError.code
    no_at_email = auth_login_t("magrathea.lost", "the_meaning_of_everything_is_42")
    assert no_at_email.status_code == InputError.code

def test_login_incorrect_password(reset_data, register_valid):
    wrong_pwd = auth_login_t("heart@of.gold", "42_is_the_answer")
    assert wrong_pwd.status_code == InputError.code

def test_login_no_password(reset_data, register_valid):
    no_pwd = auth_login_t("heart@of.gold", "")
    assert no_pwd.status_code == InputError.code

def test_login_valid(reset_data, register_valid):
    login_valid = auth_login_t("heart@of.gold", "the_meaning_of_everything_is_42")
    assert login_valid.status_code == 200
    response_data = login_valid.json()

    assert "token" in response_data
    assert "auth_user_id" in response_data

###############################################################################

def test_logout_valid(reset_data, register_valid):
    logout = auth_logout_t(register_valid["token"])
    assert logout.status_code == 200
    
def test_logout_session_twice(reset_data, register_valid):
    logout = auth_logout_t(register_valid["token"])
    assert logout.status_code == 200
    logout2 = auth_logout_t(register_valid["token"])
    assert logout2.status_code == AccessError.code

def test_logout_invalid(reset_data, register_valid):
    logout = auth_logout_t(register_valid["token"] + "DEADBEEF")
    assert logout.status_code == AccessError.code