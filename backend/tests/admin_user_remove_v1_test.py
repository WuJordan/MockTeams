import pytest
import requests
import json
from src import config
from src.error import AccessError, InputError
from tests.helper_for_tests import (admin_user_remove_t, admin_userpermission_change_t, user_profile_t, 
    auth_register_t, channels_create_t, channel_join_t, message_send_t, channel_messages_t, user_profile_sethandle_t)

@pytest.fixture
def reset_data():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def register_valid():
    return auth_register_t("heart@of.gold", "the_meaning_of_everything_is_42", "arthur", "dent").json()

@pytest.fixture
def register_second():
    return auth_register_t("email@of.gold", "the_meaning_of_everything_is_42", "arthur", "dent").json()

def test_remove_user_valid(reset_data, register_valid, register_second):
    user_delete = admin_user_remove_t(register_valid["token"], register_second["auth_user_id"])
    assert user_delete.status_code == 200

def test_remove_user_twice(reset_data, register_valid, register_second):
    user_delete = admin_user_remove_t(register_valid["token"], register_second["auth_user_id"])
    assert user_delete.status_code == 200
    user_delete2 = admin_user_remove_t(register_valid["token"], register_second["auth_user_id"])
    assert user_delete2.status_code == InputError.code

def test_remove_user_given_not_global_owner_token(reset_data, register_valid, register_second):
    user_delete = admin_user_remove_t(register_second["token"], register_valid["auth_user_id"])
    assert user_delete.status_code == AccessError.code

def test_remove_global_owner(reset_data, register_valid, register_second):
    admin_userpermission_change_t(register_valid["token"], register_second["auth_user_id"], 1)
    user_delete = admin_user_remove_t(register_second["token"], register_valid["auth_user_id"])
    assert user_delete.status_code == 200

def test_remove_invalid_user(reset_data, register_valid):
    user_delete = admin_user_remove_t(register_valid["token"], register_valid["auth_user_id"] + 1)
    assert user_delete.status_code == InputError.code

def test_remove_only_global_owner(reset_data, register_valid):
    user_delete = admin_user_remove_t(register_valid["token"], register_valid["auth_user_id"])
    assert user_delete.status_code == InputError.code

def test_message_output_remove_user(reset_data, register_valid, register_second):
    channel = channels_create_t(register_valid["token"], "test", True).json()
    channel_join_t(register_second["token"], channel["channel_id"])

    message = message_send_t(register_second["token"], channel["channel_id"], "never gonna give you up").json()
    message_id = int(message["message_id"])
    admin_user_remove_t(register_valid["token"], register_second["auth_user_id"])

    channel_messages = channel_messages_t(register_valid["token"], channel["channel_id"], 0)
    messages = channel_messages.json()
    found_msg = False
    for message in messages["messages"]:
        if message["message_id"] == message_id:
            assert message["message"] == "Removed user"
            found_msg = True
            break
    assert found_msg == True

def test_message_output_remove_user_multiple_messages(reset_data, register_valid, register_second):
    channel = channels_create_t(register_second["token"], "test", True).json()
    channel_join_t(register_valid["token"], channel["channel_id"])

    message1 = message_send_t(register_second["token"], channel["channel_id"], "never gonna give you up").json()
    message1_id = int(message1["message_id"])
    message2 = message_send_t(register_valid["token"], channel["channel_id"], "never gonna let you down").json()
    message2_id = int(message2["message_id"])
    admin_user_remove_t(register_valid["token"], register_second["auth_user_id"])

    channel_messages = channel_messages_t(register_valid["token"], channel["channel_id"], 0)
    messages = channel_messages.json()
    found_msg1 = False
    found_msg2 = False
    for message in messages["messages"]:
        if message["message_id"] == message1_id:
            assert message["message"] == "Removed user"
            found_msg1 = True
        if message["message_id"] == message2_id:
            assert message["message"] == "never gonna let you down"
            found_msg2 = True

    assert found_msg1 == True and found_msg2 == True

def test_user_profile_removed(reset_data, register_valid, register_second):
    admin_user_remove_t(register_valid["token"], register_second["auth_user_id"])
    user_profile = user_profile_t(register_valid["token"], register_second["auth_user_id"]).json()
    assert user_profile["user"]["name_first"] == "Removed"
    assert user_profile["user"]["name_last"] == "user"

def test_email_reusable(reset_data, register_valid, register_second):
    admin_user_remove_t(register_valid["token"], register_second["auth_user_id"])
    register = auth_register_t("email@of.gold", "the_meaning_of_everything_is_42", "arthur", "dent")
    assert register.status_code == 200

def test_handle_reusable(reset_data, register_valid, register_second):
    user_profile_sethandle_t(register_second["token"], "foobar")
    original_handle_profile = user_profile_t(register_valid["token"], register_second["auth_user_id"]).json()
    assert original_handle_profile["user"]["handle_str"] == "foobar"

    admin_user_remove_t(register_valid["token"], register_second["auth_user_id"])
    user_profile_sethandle_t(register_valid["token"], "foobar")
    reuse_handle_profile = user_profile_t(register_valid["token"], register_valid["auth_user_id"]).json()
    assert reuse_handle_profile["user"]["handle_str"] == "foobar"
