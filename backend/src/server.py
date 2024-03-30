import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
import hashlib
from src.error import InputError, AccessError
from src import config
from src.other import clear_v1
from src.auth import auth_login_v1, auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_messages_v1, channel_invite_v1
from src.token import decode, check_valid_token
from src.admin import admin_userpermission_change_implement, admin_user_remove_implement
from src.user import user_profile_sethandle_implement, user_profile_setname_implement, user_profile_setemail_implement
from src.channel import channel_details_v1, channel_join_v1
from src.channel_edit import channel_leave, channel_addowner, channel_removeowner
from src.channels import channels_list_v1, channels_listall_v1
from src.dm import dm_create, dm_list, dm_details, dm_remove, dm_messages, dm_leave, message_senddm
from src.message import message_send, message_remove, message_edit
from src.user import user_profile_implement, users_all_implement
from src.persistence import save_persistence
from src.data_store import data_store
import pickle

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

try:
    data = pickle.load(open("datastore.p", "rb"))
    store = data_store.get()
    store = data
    data_store.set(store)
except Exception:
    pass

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

def hash(string):
    return hashlib.sha256(string.encode()).hexdigest()

@APP.route("/auth/login/v2", methods=['POST'])
def auth_login_v2():
    user_data = request.get_json()
    login_user = auth_login_v1(user_data["email"], hash(user_data["password"]))
    save_persistence()
    return dumps(login_user)

@APP.route("/auth/register/v2", methods=['POST'])
def auth_register_v2():
    user_data = request.get_json()
    if len(user_data["password"]) < 6:
        raise InputError(description="Invalid password, must be at least 6 characters")
    new_user = auth_register_v1(user_data["email"], hash(user_data["password"]), user_data["name_first"], user_data["name_last"])
    save_persistence()
    return dumps(new_user)

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_v2():
    channel_data = request.get_json()
    user_data = decode(channel_data['token'])
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    new_channel = channels_create_v1(user_data["user_id"], channel_data["name"], channel_data["is_public"])
    save_persistence()
    return dumps(new_channel)

@APP.route("/channels/list/v2", methods=['GET'])
def channels_list_v2():
    user_data = decode(request.args.get('token'))
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    user_id = user_data['user_id']
    channels_list = channels_list_v1(user_id)
    save_persistence()
    return dumps(channels_list)
   
@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall_v2():
    user_data = decode(request.args.get('token'))
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    user_id = user_data['user_id']
    channels_list = channels_listall_v1(user_id)
    save_persistence()
    return dumps(channels_list)

@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_v2():
    user_data = decode(request.args.get('token'))
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')

    channel_id = int(request.args.get('channel_id'))
    user_id = user_data['user_id']
    details = channel_details_v1(user_id, channel_id)
    save_persistence()
    return dumps(details)
    

# channel/join/v2
@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_v2():
    channel_data = request.get_json()
    token = channel_data['token']
    user_data = decode(token)
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')

    channel_id = channel_data['channel_id']
    user_id = user_data['user_id']
    join = channel_join_v1(user_id, channel_id)
    save_persistence()
    return dumps(join)

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_v2():
    invite_data = request.get_json()
    user_data = decode(invite_data['token'])
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    save_persistence()
    return dumps(channel_invite_v1(user_data["user_id"], invite_data["channel_id"], invite_data["u_id"]))

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages_v2():
    user_data = decode(request.args.get('token'))
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    messages = channel_messages_v1(user_data["user_id"], channel_id, start)
    save_persistence()
    return dumps(messages)

@APP.route("/clear/v1", methods=['DELETE'])
def clear_v2():
    clear_v1()
    save_persistence()
    return dumps({})

@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout_v1():
    token = request.get_json()
    token = decode(token["token"])

    user = check_valid_token(token)
    if user:
        user["sessions"].remove(token["session"])
    else:
        raise AccessError(description='Invalid token')
    save_persistence()
    return dumps({})

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave_v1():
    channel_data = request.get_json()
    user_data = decode(channel_data['token'])
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    save_persistence()
    return dumps(channel_leave(user_data["user_id"], channel_data["channel_id"]))

@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner_v1():
    data = request.get_json()
    token = decode(data["token"])

    user = check_valid_token(token)
    if user:
        channel_addowner(user, data["channel_id"], data["u_id"])
    else:
        raise AccessError(description='Invalid token')
    save_persistence()
    return dumps({})

@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner_v1():
    data = request.get_json()
    token = decode(data["token"])

    user = check_valid_token(token)
    if user:
        channel_removeowner(user, data["channel_id"], data["u_id"])
    else:
        raise AccessError(description='Invalid token')
    save_persistence()
    return dumps({})

@APP.route("/message/send/v1", methods=['POST'])
def message_send_v1():
    message_data = request.get_json()
    user_data = decode(message_data['token'])
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    save_persistence()
    return dumps(message_send(user_data["user_id"], message_data["channel_id"], message_data["message"]))

@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit_v1():
    message_data = request.get_json()
    user_data = decode(message_data['token'])
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    save_persistence()
    return dumps(message_edit(user_data["user_id"], message_data["message_id"], message_data["message"]))

@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove_v1():
    message_data = request.get_json()
    user_data = decode(message_data['token'])
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    save_persistence()
    return dumps(message_remove(user_data["user_id"], message_data["message_id"]))

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create_v1():
    dm_data = request.get_json()
    token = decode(dm_data['token'])
    
    user = check_valid_token(token)
    if user:
        save_persistence()
        return dumps(dm_create(user, dm_data["u_ids"]))
    else:
        raise AccessError(description='Invalid token')

# dm/list/v1
@APP.route("/dm/list/v1", methods=['GET'])
def dm_list_v1():
    user_data = decode(request.args.get('token'))
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    
    user_id = user_data['user_id']
    save_persistence()
    return dumps(dm_list(user_id))

        


@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove_v1():
    dm_data = request.get_json()
    token = decode(dm_data['token'])
    
    user = check_valid_token(token)
    if user:
        save_persistence()
        return dumps(dm_remove(user, dm_data["dm_id"]))
    else:
        raise AccessError(description='Invalid token')

@APP.route("/dm/details/v1", methods=['GET'])
def dm_details_v1():
    user_data = decode(request.args.get('token'))
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')

    user_id = user_data['user_id']
    dm_id = int(request.args.get('dm_id'))
    save_persistence()
    return dumps(dm_details(user_id, dm_id))

# dm/leave/v1
@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave_v1():
    dm_data = request.get_json()
    user_data = decode(dm_data['token'])
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    save_persistence()
    return dumps(dm_leave(user_data["user_id"], dm_data["dm_id"]))

# dm/messages/v1
@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages_v1():
    user_data = decode(request.args.get('token'))
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))
    dm_message = dm_messages(user_data['user_id'], dm_id, start)
    save_persistence()
    return dumps(dm_message)

# message/senddm/v1
@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm_v1():
    message_data = request.get_json()
    user_data = decode(message_data['token'])
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    save_persistence()
    return dumps(message_senddm(user_data["user_id"], message_data["dm_id"], message_data["message"]))

@APP.route("/users/all/v1", methods=['GET'])
def users_all_v1():
    user_data = decode(request.args.get('token'))
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    users_all = users_all_implement()
    save_persistence()
    return dumps(users_all)

@APP.route("/user/profile/v1", methods=['GET'])
def user_profile_v1():
    user_data = decode(request.args.get('token'))
    if user_data is None or not check_valid_token(user_data):
        raise AccessError(description='Invalid token')
    user_id = int(request.args.get('u_id'))
    user_profile = user_profile_implement(user_id)
    save_persistence()
    return dumps(user_profile)
    

@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_profile_setname_v1():
    data = request.get_json()
    token = decode(data["token"])

    user = check_valid_token(token)
    if user:
        user_profile_setname_implement(user, data["name_first"], data["name_last"])
    else:
        raise AccessError(description='Invalid token')
    save_persistence()
    return dumps({})

@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_profile_setemail_v1():
    data = request.get_json()
    token = decode(data["token"])

    user = check_valid_token(token)
    if user:
        user_profile_setemail_implement(user, data["email"])
    else:
        raise AccessError(description='Invalid token')
    save_persistence()
    return dumps({})

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_profile_sethandle_v1():
    data = request.get_json()
    token = decode(data["token"])

    user = check_valid_token(token)
    if user:
        user_profile_sethandle_implement(user, data["handle_str"])
    else:
        raise AccessError(description='Invalid token')
    save_persistence()
    return dumps({})


@APP.route("/admin/user/remove/v1", methods=["DELETE"])
def admin_user_remove_v1():
    data = request.get_json()
    token = decode(data["token"])

    user = check_valid_token(token)
    if not user:
        raise AccessError(description='Invalid token')
    if user and not user["is_owner"]:
        raise AccessError(description='Authorised user is not a global owner')

    admin_user_remove_implement(data["u_id"])
    save_persistence()
    return dumps({})

@APP.route("/admin/userpermission/change/v1", methods=["POST"])
def admin_userpermission_change_v1():
    data = request.get_json()
    token = decode(data["token"])

    user = check_valid_token(token)
    if not user:
        raise AccessError(description='Invalid token')
    if user and not user["is_owner"]:
        raise AccessError(description='Authorised user is not a global owner')

    admin_userpermission_change_implement(data["u_id"], data["permission_id"])
    save_persistence()
    return dumps({})




#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
