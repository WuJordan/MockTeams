from src.data_store import data_store
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from src.channel import check_valid_id

def check_channel_name(name):
    '''
    Checks if the name given is within the 1-20 (inclusive) character limit

    Arguments:
        name        str         - Name of channel

    Exceptions:
        InputError  - Occurs when name is not within the character limit

    Return Value:
        N/A
    '''
    if len(name) < 1 or len(name) > 20:
        raise InputError(description="Invalid name, must be within 1-20 characters (inclusive)")

def channels_list_v1(auth_user_id):

    '''
    Provide a list of all channels (and their associated details) that the authorised user is part of.

    Arguments:
        auth_user_id    int    - User ID of the user who is making the request
    
    Exceptions:
        None

    Return Value:
        Returns list of channels dict (contains channel_id and name) on the condition that the user is a member.   

    '''

    store = data_store.get()
   
    member_of_channel_list = {
        'channels': []
    }
    
    for channel in store['channels']: 
        for members in channel['all_members']: 
            if members['user_id'] == auth_user_id:
                member_of_channel_list['channels'].append({
                    'channel_id' : channel['channel_id'],
                    'name' : channel['name'],
                })
        
    return member_of_channel_list


def channels_listall_v1(auth_user_id):

    '''
    Provide a list of all channels, including private channels, (and their associated details).

    Arguments:
        auth_user_id    int    - User ID of the user who is making the request
    
    Exceptions:
        None

    Return Value:
        Returns a list of all channels dict (contains channel_id and name) on the condition the user_id is valid.

    '''

    store = data_store.get()

    all_channels_list = {
        'channels': []
    }

    for channel in store['channels']:
        all_channels_list['channels'].append({
            'channel_id' : channel['channel_id'],
            'name' : channel['name'],
        }) 

    return all_channels_list


def channels_create_v1(auth_user_id, name, is_public):
    '''
    Creates a new channel into the Seams database

    Arguments:
        auth_user_id    int     - User ID of user who is making request
        name            str     - Name of channel must be within 1-20 characters inclusive
        is_public       bool    - Indicator for public or private

    Exceptions:
        InputError  - Occurs when length of name is less than 1 or more than 20 characters

    Return Value:
        Returns { channel_id } on successful creation of channel
    '''
    store = data_store.get()
    auth_user = check_valid_id(auth_user_id, store)

    check_channel_name(name)

    new_id = len(store['channels'])
    store['channels'].append({
        'channel_id': new_id,
        'name': name,
        'is_public': is_public,
        'owner_members': [auth_user],
        'all_members': [auth_user],
        'messages': [],
    })
    data_store.set(store)
    return {
        'channel_id': new_id,
    }
