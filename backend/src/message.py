from src.data_store import data_store
from src.error import InputError, AccessError
from src.channel import get_channel, user_in_channel, check_valid_id
from datetime import timezone
import datetime

def change_message(user, message_id, chats, is_edit, message):
    '''
    Edits or removes message with message_id, from either DM or channel

    Arguments:
        user            dict    - User who is making request
        message_id      int     - Message ID of message requested
        chats           str     - Either "dms" or "channels"
        is_edit         bool    - Indicates whether message is to be edited or removed
        message         str     - Content of message (if is_edit is true)
    
    Exceptions:
        Input Error     - Occurs when message_id does not refer to a valid message
                          within a channel/DM that the authorised user has joined
                        - Occurs when length of message is over 1000 characters (edit)
        Access Error    - Occurs when message_id is valid but authorised user is not sender
                          and does not have owner permissions
    Return Value: 
        NA
    '''
    store = data_store.get()
    for chat in store[chats]:
        if user in chat["all_members"]:
            for msg in chat['messages']:
                if msg['message_id'] == message_id:
                    if msg['user_id'] != user['user_id'] and user not in chat['owner_members'] and chats == 'dms':
                        raise AccessError(description='User is not sender nor has owner permissions in dm')
                    if msg['user_id'] != user['user_id'] and not (user in chat['owner_members'] or user['is_owner']):
                        raise AccessError(description='User is not sender nor has owner permissions in channel')
                    if is_edit and len(message) > 1000:
                        raise InputError(description="Length of message is over 1000 characters")
                    if is_edit:
                        msg['message'] = message
                        data_store.set(store)
                        return
                    chat['messages'].remove(msg)
                    data_store.set(store)
                    return
    
    raise InputError(description="Invalid message within channel/DM that user has joined")

def message_send(auth_user_id, channel_id, message):
    '''
    Send a message from authorised user to channel with channel_id.
    
    Arguments:
        auth_user_id    int     - User ID of user who is making request
        channel_id      int     - Channel ID of channel requested
        message         str     - Content of message

    Exceptions:
        Input Error     - Occurs when channel_id does not refer to a valid channel
                        - Occurs when length of message is less than 1 or over 1000 characters
        Access Error    - Occurs when channel_id is valid but authorised user is not a member of the channel

    Return Value: 
        Returns { message_id } on success
    '''
    store = data_store.get()

    channel = get_channel(channel_id, store)
    if not channel:
        raise InputError(description="Invalid channel")

    if not user_in_channel(channel, auth_user_id):
        raise AccessError(description="User is not a member of the channel")

    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="Length of message is less than 1 or over 1000 characters")

    new_id = store['message_count']
    store['message_count'] += 1
    channel["messages"].insert(
        0,
        {
            'message_id': new_id,
            'user_id': auth_user_id,
            'message': message,
            'time_sent': int(datetime.datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp()),
        }
    )
    data_store.set(store)
    return { 'message_id': new_id }

def message_edit(auth_user_id, message_id, message):
    '''
    Edit a message with message_id from authorised user.
    
    Arguments:
        auth_user_id    int     - User ID of user who is making request
        message_id      int     - Message ID of message requested for editing
        message         str     - Content of message

    Exceptions:
        Input Error     - Occurs when length of message is over 1000 characters
                        - Occurs when message_id does not refer to a valid message
                          within a channel/DM that the authorised user has joined
        Access Error    - Occurs when message_id is valid but authorised user is not sender
                          and does not have owner permissions

    Return Value: 
        Returns {} on success
    '''
    store = data_store.get()
    user = check_valid_id(auth_user_id, store)
    if not len(message):
        try:
            change_message(user, message_id, 'channels', False, None)
        except Exception:
            change_message(user, message_id, 'dms', False, None)
    else:
        try:
            change_message(user, message_id, 'channels', True, message)
        except Exception:
            change_message(user, message_id, 'dms', True, message)
    return {}

def message_remove(auth_user_id, message_id):
    '''
    Remove a message with message_id from authorised user.
    
    Arguments:
        auth_user_id    int     - User ID of user who is making request
        message_id      int     - Message ID of message requested for removing

    Exceptions:
        Input Error     - Occurs when message_id does not refer to a valid message
                          within a channel/DM that the authorised user has joined
        Access Error    - Occurs when message_id is valid but authorised user is not sender
                          and does not have owner permissions

    Return Value: 
        Returns {} on success
    '''
    store = data_store.get()
    user = check_valid_id(auth_user_id, store)

    try:
        change_message(user, message_id, 'channels', False, None)
    except Exception:
        change_message(user, message_id, 'dms', False, None)

    return {}
