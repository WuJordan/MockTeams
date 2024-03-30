from src.data_store import data_store
from src.error import InputError, AccessError
from src.channel import get_channel, user_in_channel, check_valid_id

def channel_leave(auth_user_id, channel_id):
    '''
    Given a channel with ID channel_id that the given user is a member of, 
    remove them as a member of the channel. 
    
    Arguments:
        auth_user_id    int     - User ID of user who is making request
        channel_id      int     - Channel ID of channel requested

    Exceptions:
        Input Error     - Occurs when channel_id does not refer to a valid channel
        Access Error    - Occurs when channel_id is valid but authorised user is not a member of the channel

    Return Value: 
        Returns {} on success
    '''
    store = data_store.get()
    auth_user = check_valid_id(auth_user_id, store)

    channel = get_channel(channel_id, store)
    if not channel:
        raise InputError(description="Invalid channel")

    if not user_in_channel(channel, auth_user_id):
        raise AccessError(description="User is not a member of the channel")
    
    try:
        channel['owner_members'].remove(auth_user)
    except ValueError:
        pass
    channel['all_members'].remove(auth_user)
    data_store.set(store)
    return {}

def channel_addowner(auth_user, channel_id, u_id):
    '''
    Given a channel with ID channel_id that the given auth_user is a member of, 
    make user with u_id an owner of channel. 
    
    Arguments:
        auth_user       dict    - User who is making request
        channel_id      int     - Channel ID of channel requested
        u_id            int     - User id of person requested to become owner of channel

    Exceptions:
        Input Error     - Occurs when channel_id does not refer to a valid channel, 
                          u_id is invalid, u_id is not a member, u_id is already owner of channel
        Access Error    - Occurs when channel_id is valid but authorised user does not have owner permissions in the channel

    Return Value: 
        NA
    '''
    store = data_store.get()

    channel = get_channel(channel_id, store)
    if not channel:
        raise InputError(description="Invalid channel")

    if auth_user not in channel["owner_members"] and not auth_user["is_owner"]:
        raise AccessError(description="Auth user has no owner permissions")

    target_user = check_valid_id(u_id, store)
    if not target_user:
        raise InputError(description="User with u_id does not refer to a valid user")

    if not user_in_channel(channel, u_id):
        raise InputError(description="User with u_id is not a member of the channel")

    if target_user in channel["owner_members"]:
        raise InputError(description="User with u_id already owner")

    channel['owner_members'].append(target_user)
    data_store.set(store)

def channel_removeowner(auth_user, channel_id, u_id):
    '''
    Given a channel with ID channel_id that the given auth_user is a member of, 
    remove user with u_id as an owner of the channel. 
    
    Arguments:
        auth_user       dict    - User who is making request
        channel_id      int     - Channel ID of channel requested
        u_id            int     - User id of person requested to become owner of channel

    Exceptions:
        Input Error     - Occurs when channel_id does not refer to a valid channel, 
                          u_id is invalid, u_id is not an owner, u_id is the only owner of channel
        Access Error    - Occurs when channel_id is valid but authorised user does not have owner permissions in the channel

    Return Value: 
        NA
    '''
    store = data_store.get()

    channel = get_channel(channel_id, store)
    if not channel:
        raise InputError(description="Invalid channel")
    
    if auth_user not in channel["owner_members"] and not auth_user["is_owner"]:
        raise AccessError(description="Auth user has no owner permissions")

    target_user = check_valid_id(u_id, store)
    if not target_user:
        raise InputError(description="User with u_id does not refer to a valid user")

    if target_user not in channel["owner_members"]:
        raise InputError(description="User with u_id is no an owner of the channel")

    if target_user in channel["owner_members"] and len(channel["owner_members"]) == 1:
        raise InputError(description="User with u_id is the only owner of the channel")

    channel['owner_members'].remove(target_user)
    data_store.set(store)
