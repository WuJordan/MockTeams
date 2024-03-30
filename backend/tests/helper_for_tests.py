import requests
from src import config

def auth_login_t(email, password):
    return requests.post(
        config.url + "auth/login/v2",
        json={
            "email": email,
            "password": password
        }
    )

def auth_register_t(email, password, name_first, name_last):
    return requests.post(
        config.url + "auth/register/v2",
        json={
            "email": email,
            "password": password,
            "name_first": name_first,
            "name_last": name_last
        }
    )

def channels_create_t(token, name, is_public):
    return requests.post(
        config.url + "channels/create/v2",
        json={
            "token": token,
            "name": name,
            "is_public": is_public
        }
    )

def channels_list_t(token):
    return requests.get(
        config.url + "channels/list/v2",
        params={
            "token": token
        }
    )

def channels_listall_t(token):
    return requests.get(
        config.url + "channels/listall/v2",
        params={
            "token": token
        }
    )

def channel_details_t(token, channel_id):
    return requests.get(
        config.url + "channel/details/v2",
        params={
            "token": token,
            "channel_id": channel_id
        }
    )

def channel_join_t(token, channel_id):
    return requests.post(
        config.url + "channel/join/v2",
        json={
            "token": token,
            "channel_id": channel_id
        }
    )

def channel_invite_t(token, channel_id, u_id):
    return requests.post(
        config.url + "channel/invite/v2",
        json={
            "token": token,
            "channel_id": channel_id,
            "u_id": u_id
        }
    )

def channel_messages_t(token, channel_id, start):
    return requests.get(
        config.url + "channel/messages/v2",
        params={
            "token": token,
            "channel_id": channel_id,
            "start": start
        }
    )

def auth_logout_t(token):
    return requests.post(
        config.url + "auth/logout/v1",
        json={
            "token": token
        }
    )

def channel_leave_t(token, channel_id):
    return requests.post(
        config.url + "channel/leave/v1",
        json={
            "token": token,
            "channel_id": channel_id
        }
    )

def channel_addowner_t(token, channel_id, u_id):
    return requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": token,
            "channel_id": channel_id,
            "u_id": u_id
        }
    )

def channel_removeowner_t(token, channel_id, u_id):
    return requests.post(
        config.url + "channel/removeowner/v1",
        json={
            "token": token,
            "channel_id": channel_id,
            "u_id": u_id
        }
    )

def message_send_t(token, channel_id, message):
    return requests.post(
        config.url + "message/send/v1",
        json={
            "token": token,
            "channel_id": channel_id,
            "message": message
        }
    )

def message_edit_t(token, message_id, message):
    return requests.put(
        config.url + "message/edit/v1",
        json={
            "token": token,
            "message_id": message_id,
            "message": message
        }
    )

def message_remove_t(token, message_id):
    return requests.delete(
        config.url + "message/remove/v1",
        json={
            "token": token,
            "message_id": message_id
        }
    )

def dm_create_t(token, u_ids):
    return requests.post(
        config.url + "dm/create/v1",
        json={
            "token": token,
            "u_ids": u_ids
        }
    )

def dm_list_t(token):
    return requests.get(
        config.url + "dm/list/v1",
        params={
            "token": token
        }
    )

def dm_remove_t(token, dm_id):
    return requests.delete(
        config.url + "dm/remove/v1",
        json={
            "token": token,
            "dm_id": dm_id
        }
    )

def dm_details_t(token, dm_id):
    return requests.get(
        config.url + "dm/details/v1",
        params={
            "token": token,
            "dm_id": dm_id
        }
    )

def dm_leave_t(token, dm_id):
    return requests.post(
        config.url + "dm/leave/v1",
        json={
            "token": token,
            "dm_id": dm_id
        }
    )

def dm_messages_t(token, dm_id, start):
    return requests.get(
        config.url + "dm/messages/v1",
        params={
            "token": token,
            "dm_id": dm_id,
            "start": start
        }
    )

def message_senddm_t(token, dm_id, message):
    return requests.post(
        config.url + "message/senddm/v1",
        json={
            "token": token,
            "dm_id": dm_id,
            "message": message
        }
    )

def users_all_t(token):
    return requests.get(
        config.url + "users/all/v1",
        params={
            "token": token
        }
    )

def user_profile_t(token, u_id):
    return requests.get(
        config.url + "user/profile/v1",
        params={
            "token": token,
            "u_id": u_id
        }
    )

def user_profile_setname_t(token, name_first, name_last):
    return requests.put(
        config.url + "user/profile/setname/v1",
        json={
            "token": token,
            "name_first": name_first,
            "name_last": name_last
        }
    )

def user_profile_setemail_t(token, email):
    return requests.put(
        config.url + "user/profile/setemail/v1",
        json={
            "token": token,
            "email": email
        }
    )

def user_profile_sethandle_t(token, handle_str):
    return requests.put(
        config.url + "user/profile/sethandle/v1",
        json={
            "token": token,
            "handle_str": handle_str
        }
    )

def admin_user_remove_t(token, u_id):
    return requests.delete(
        config.url + "admin/user/remove/v1",
        json={
            "token": token,
            "u_id": u_id
        }
    )

def admin_userpermission_change_t(token, u_id, permission_id):
    return requests.post(
        config.url + "admin/userpermission/change/v1",
        json={
            "token": token,
            "u_id": u_id,
            "permission_id": permission_id
        }
    )
