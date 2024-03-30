from src.data_store import data_store
from src.error import InputError, AccessError

def omit_irrelevant_keys(channel, members_string):
    '''
    Omits irrelevant keys for each user for output and returns list of members with modified users

    Arguments:
        channel           dict        - Channel containing list of members
        members_string    string      - Indicates type of members list being modified

    Exceptions:
        N/A

    Return Value:
        Returns members_modified (list of users with omitted keys) on success
    '''
    members_modified = []
    members = channel[members_string]
    for member in members:
        member_modified = {
            'u_id': member['user_id'],
            'email': member['email'],
            'name_first': member['name_first'],
            'name_last': member['name_last'],
            'handle_str': member['user_handle'],
        }
        members_modified.append(member_modified) 
    return members_modified

def check_valid_id(auth_user_id, store):
    '''
    Checks if auth_user_id given is valid and returns its user if found

    Arguments:
        auth_user_id    int         - User ID of the user who is making the request
        store           dict        - Database of Seams information

    Exceptions:
        N/A

    Return Value:
        Returns user dict on success in finding given user
        Returns empty dict on failure in finding given user
    '''
    for user in store['users']:
        if user['user_id'] == auth_user_id and user['is_active']:
            return user

    return {}

def user_in_channel(channel, auth_user_id):
    '''
    Given a channel and a particular user_id returns if user is a member of the channel

    Arguments:
        auth_user_id    int     - User ID of user who is making request
        channel         dict    - Dictionary of a particular channel and its details

    Exceptions:
        N/A

    Return Value: 
        Returns True if user is a member of the channel
        Returns False if user is not a member of the channel
    '''
    for user in channel["all_members"]:
        if auth_user_id == user["user_id"]:
            return True
    return False

def get_channel(channel_id, store):
    '''
    Given a channel_id, returns the requested { channel }

    Arguments:
        channel_id      int         - Channel ID of requested channel
        store           dict        - Database of Seams information

    Exceptions:
        N/A

    Return Value:
        Returns channel dict on success in finding given channel
        Returns empty dict on failure in finding given channel
    '''

    channels = store["channels"]
    for channel in channels:
        if channel["channel_id"] == channel_id:
            return channel
    return {}

def channel_invite_v1(auth_user_id, channel_id, u_id):
    '''
    Invites user with u_id to join channel with channel_id, if authorised user is a member

    Arguments:
        auth_user_id    int         - User ID of the user who is making the request
        channel_id      int         - Channel ID of channel requested for invitation
        u_id            int         - User ID of the user invited to join channel

    Exceptions:
        InputError  - Occurs when channel_id is invalid, u_id is invalid or user with u_id is already a member
        AccessError - Occurs when channel_id is valid but authorised user is not a member

    Return Value:
        Returns {} on successful invite for user with u_id into channel with channel_id
    '''

    store = data_store.get()

    channel = get_channel(channel_id, store)
    if not channel:
        raise InputError(description="Invalid channel")

    if not user_in_channel(channel, auth_user_id):
        raise AccessError(description="Authorised user is not a member of the channel")

    invited_user = check_valid_id(u_id, store)
    if not invited_user:
        raise InputError(description="Invalid u_id")

    if user_in_channel(channel, u_id):
        raise InputError(description="User with u_id already a member")
    
    channel['all_members'].append(invited_user)
    data_store.set(store)
    return {}

def channel_details_v1(auth_user_id, channel_id):
    '''
    Provides basic details of channel that authorised user is a member of

    Arguments:
        auth_user_id    int     - User ID of user who is making request
        channel_id      int     - Channel ID of channel requested for details

    Exceptions:
        InputError  - Occurs when channel_id is invalid
        AccessError - Occurs when channel_id is valid but user is not a member

    Return Value:
        Returns { name, is_public, owner_members, all_members } on valid channel with valid auth user as member
    '''
    store = data_store.get()

    channel = get_channel(channel_id, store)
    if not channel:
        raise InputError(description="Invalid channel")

    if not user_in_channel(channel, auth_user_id):
        raise AccessError(description="Authorised user is not a member of the channel")

    all_members = omit_irrelevant_keys(channel, "all_members")
    owner_members = omit_irrelevant_keys(channel, "owner_members")
    return {
        'name': channel['name'],
        'is_public': channel['is_public'], 
        'owner_members': owner_members,
        'all_members': all_members
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    '''
    Given a channel with ID channel_id that the given user is a member of, 
    return up to 50 messages between index "start" and "start + 50". 
    
    Arguments:
        auth_user_id    int     - User ID of user who is making request
        channel_id      int     - Channel ID of channel requested for details
        start           int     - Index of the newest message to be returned

    Exceptions:
        Input Error     - Occurs when channel_id does not refer to a valid channel
                        - Occurs when start is greater than the total number of messages in the channel
        Access Error    - Occurs when channel_id is valid but authorised user is not a member of the channel

    Return Value: 
        Returns { messages } as a list of dictionaries, where each dictionary contains types { message_id, u_id, message, time_sent }
        Returns start (Starting index that user gave)
        Returns end index as start + 50, or -1 if it also returns the least recent messages, as an indication there are no more messages to return
    '''
    store = data_store.get()

    channel = get_channel(channel_id, store)
    if not channel:
        raise InputError(description="Invalid channel")

    if not user_in_channel(channel, auth_user_id):
        raise AccessError(description="User is not a member of the channel")

    final_msg = len(channel["messages"])
    if final_msg < start:
        raise InputError(description="Start greater than total number of messages in channel")

    end = start + 50 if (start + 50 < final_msg) else final_msg

    message_list = []
    for message in channel["messages"][start:end]:
        message_list.append({
            "message_id" : message["message_id"],
            "u_id" : message["user_id"],
            "message" : message["message"],
            "time_sent" : message["time_sent"],
        })
    return {"messages" : message_list, "start" : start, "end" : end if (end == start + 50) else -1}

def channel_join_v1(auth_user_id, channel_id):
    '''
    Adds authorised user into channel with a given channel_id

    Arguments:
        auth_user_id    int     - User ID of user who is making request
        channel_id      int     - Channel ID of channel requested for join

    Exceptions:
        InputError  - Occurs when channel_id is invalid or when authorised user is already member of channel
        AccessError - Occurs when channel_id is valid but channel is private and user is not a member and 
                      not a global owner

    Return Value:
        Returns {} on successful join for authorised user into channel with channel_id
    '''
    store = data_store.get()
    auth_user = check_valid_id(auth_user_id, store)

    channel = get_channel(channel_id, store)
    if not channel:
        raise InputError(description="Invalid channel")

    if not channel['is_public'] and not user_in_channel(channel, auth_user_id) and not auth_user['is_owner']:
        raise AccessError(description="Non global owner can't join private channel")

    if user_in_channel(channel, auth_user_id):
        raise InputError(description="Already a member")

    channel['all_members'].append(auth_user)
    data_store.set(store)
    return {}
