import pytest
import requests
import json
from src import config
from src.error import AccessError, InputError
from tests.helper_for_tests import admin_userpermission_change_t, auth_register_t

@pytest.fixture
def reset_data():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def register_valid():
    return auth_register_t("heart@of.gold", "the_meaning_of_everything_is_42", "arthur", "dent").json()

@pytest.fixture
def register_second():
    return auth_register_t("email@of.gold", "the_meaning_of_everything_is_42", "arthur", "dent").json()

def test_change_permission_owner_success(reset_data, register_valid, register_second):
    permission = admin_userpermission_change_t(register_valid["token"], register_second["auth_user_id"], 1)
    assert permission.status_code == 200

def test_change_self_permission(reset_data, register_valid, register_second):
    admin_userpermission_change_t(register_valid["token"], register_second["auth_user_id"], 1)
    permission = admin_userpermission_change_t(register_valid["token"], register_valid["auth_user_id"], 2)
    assert permission.status_code == 200

def test_change_permission_member_success(reset_data, register_valid, register_second):
    owner = admin_userpermission_change_t(register_valid["token"], register_second["auth_user_id"], 1)
    assert owner.status_code == 200
    member = admin_userpermission_change_t(register_second["token"], register_valid["auth_user_id"], 2)
    assert member.status_code == 200


def test_invalid_user(reset_data, register_valid):
    permission = admin_userpermission_change_t(register_valid["token"], register_valid["auth_user_id"] + 1, 1)
    assert permission.status_code == InputError.code

def test_u_id_only_global_owner_demoted_to_member(reset_data, register_valid):
    permission = admin_userpermission_change_t(register_valid["token"], register_valid["auth_user_id"], 2)
    assert permission.status_code == InputError.code

def test_invalid_permission_id(reset_data, register_valid, register_second):
    permission = admin_userpermission_change_t(register_valid["token"], register_second["auth_user_id"], 3)
    assert permission.status_code == InputError.code

def test_user_already_at_given_permissions_member(reset_data, register_valid, register_second):
    permission = admin_userpermission_change_t(register_valid["token"], register_second["auth_user_id"], 2)
    assert permission.status_code == InputError.code

def test_user_already_at_given_permissions_owner(reset_data, register_valid, register_second):
    permission = admin_userpermission_change_t(register_valid["token"], register_second["auth_user_id"], 1)
    assert permission.status_code == 200
    permission = admin_userpermission_change_t(register_valid["token"], register_second["auth_user_id"], 1)
    assert permission.status_code == InputError.code
      
def test_auth_user_not_global_owner(reset_data, register_valid, register_second):
    permission = admin_userpermission_change_t(register_second["token"], register_second["auth_user_id"], 1)
    assert permission.status_code == AccessError.code

def test_change_permission_owner_invalid_token(reset_data, register_valid, register_second):
    permission = admin_userpermission_change_t(register_valid["token"] + "DEADBEEF", register_second["auth_user_id"], 1)
    assert permission.status_code == AccessError.code