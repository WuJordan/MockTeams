from src.data_store import data_store
from src.error import InputError
from src.channel import check_valid_id
from src.channel import user_in_channel

def num_global_owners():
    '''
    Counts the number of global owners in Seams

    Arguments:
        N/A

    Exceptions:
        N/A

    Return Value:
        int count   - num global owners
    '''
    store = data_store.get()
    count = 0
    for user in store["users"]:
        if user["is_owner"]:
            count += 1
    assert count != 0 # we have a problem otherwise...
    return count

def remove_from_chat(user, chats, store):
    '''
    Given a user, type of chat (dm/channel) and the data store, removes the user from any chats 
    they are a member of

    Arguments:
        user            dict        - user dict from datastore of given user
        chats           str         - "dms" or "channels"

    Exceptions:
        N/A

    Return Value:
        N/A
    '''
    for chat in store[chats]:
        if user in chat["all_members"]:
            chat["all_members"].remove(user)
        if user in chat["owner_members"]:
            chat["owner_members"].remove(user)

def remove_messages(user, chats, store):
    '''
    Given a user, type of chat (dm/channel) and the data store, alters the contents of any messages
    the user has sent across Seams (including chats they were previously a part of and have since left)
    to "Removed user"

    Arguments:
        user            dict        - user dict from datastore of given user
        chats           str         - "dms" or "channels"

    Exceptions:
        N/A

    Return Value:
        N/A
    '''
    for chat in store[chats]:
        for message in chat["messages"]:
            if user["user_id"] == message["user_id"]:
                message["message"] = "Removed user"

def admin_user_remove_implement(u_id):
    '''
    Given a user_id, removes the given user and their associated data from Seams

    Arguments:
        u_id            int        - auth_user_id

    Exceptions:
        InputError  - Occurs when user doesn't exist
                    - Occurs when user is not active i.e. has already been removed
        
        AccessError - Occurs when user is the only global owner in Seams

    Return Value:
        N/A
    '''
    store = data_store.get()
    user = check_valid_id(u_id, store)
    if not user or not user["is_active"]:
        raise InputError(description="Invalid user id")
    if user["is_owner"] and num_global_owners() == 1:
        raise InputError(description="u_id refers to a user who is the only global owner")

    remove_messages(user, "dms", store)
    remove_messages(user, "channels", store)

    remove_from_chat(user, "dms", store)
    remove_from_chat(user, "channels", store)

    user["name_first"] = "Removed"
    user["name_last"] = "user"
    user["is_active"] = False
    user["email"] = None
    user["user_handle"] = None
    user["sessions"] = []
    user["is_owner"] = False

def admin_userpermission_change_implement(u_id, permission_id):
    '''
    Given a user_id and permission_id, changes the users permissions to the given id

    Arguments:
        user_id            int          - auth_user_id
        permission_id      int          - 1 or 2 to indicate owner and member respectively

    Exceptions:
        InputError  - Occurs when user doesn't exist
                    - Occurs when user is not active i.e. has already been removed
                    - Occurs when permission id is invalid
                    - User already has the permission level of the given permission id
        
        AccessError - Occurs when user is the only global owner in Seams and they are being demoted to a user
    Return Value:
        N/A
    '''
    store = data_store.get()
    user = check_valid_id(u_id, store)
    if not user or not user["is_active"]:
        raise InputError(description="Invalid user id")
    if user["is_owner"] and num_global_owners() == 1 and permission_id == 2:
        raise InputError(description="u_id refers to a user who is the only global owner and they are being demoted to a user")

    if permission_id not in [1, 2]:
        raise InputError(description="Invalid permission id")
    if (permission_id == 1 and user["is_owner"]) or (permission_id == 2 and not user["is_owner"]):
        raise InputError(description="User already has the permission level of the permission id")
      
    if permission_id == 1:
        user["is_owner"] = True
    else:
        user["is_owner"] = False
