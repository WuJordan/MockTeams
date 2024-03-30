from src.data_store import data_store
from src.error import InputError, AccessError
from src.channel import check_valid_id, omit_irrelevant_keys
from datetime import timezone
import datetime

def dm_name(user, u_ids, store):
    '''
    Generates names based on given users' handles

    Arguments:
        user            dict    - User who is making request
        u_ids           list    - List of u_id's that the DM is directed to, and will not include creator
        store           dict    - Data_store containing all users, channels, dms and messages

    Exceptions:
        None
    
    Return Value:
        Returns name of DM on succesful generation    
    '''
    handle_list = [user["user_handle"]]
    for u_id in u_ids:
        handle_list.append(check_valid_id(u_id, store)["user_handle"])
    handle_list.sort()
    return ', '.join(handle_list)

def get_dm(dm_id, store):
    '''
    Given a dm_id, returns the requested { dm }

    Arguments:
        dm_id           int         - dm ID of requested dm
        store           dict        - Database of Seams information

    Exceptions:
        N/A

    Return Value:
        Returns dm dict on success in finding given dm
        Returns empty dict on failure in finding given dm
    ''' 

    dms = store["dms"]
    for dm in dms:
        if dm["dm_id"] == dm_id:
            return dm
    return {}

def dm_create(user, u_ids):
    '''
    Creates a new dm into the Seams database

    Arguments:
        user            dict    - User who is making request
        u_ids           list    - List of u_id's that the DM is directed to, and will not include creator

    Exceptions:
        InputError  - Occurs when any u_id in u_ids does not refer to a valid user
                    - Occurs when there are duplicate u_id's in u_ids

    Return Value:
        Returns { dm_id } on successful creation of dm
    '''
    store = data_store.get()

    if any(not check_valid_id(u_id, store) for u_id in u_ids):
        raise InputError(description="Any u_id in u_ids does not refer to a valid user")

    if len(set(u_ids)) != len(u_ids):
        raise InputError(description="There are duplicate u_id's in u_ids")

    name = dm_name(user, u_ids, store)

    new_id = store['dm_count']
    store['dm_count'] += 1
    dm = {
        'dm_id': new_id,
        'name': name,
        'owner_members': [user],
        'all_members': [user],
        'messages': [],
    }
    for u_id in u_ids:
        dm["all_members"].append(check_valid_id(u_id, store))
    store['dms'].append(dm)
    data_store.set(store)
    return {
        'dm_id': new_id,
    }

def dm_list(auth_user_id):  
    
    '''
    Returns the list of DMs that the user is a member of.

    Arguments:
        auth_user_id    int     - User ID of the user who is making the request

    Exceptions:
        None

    Return Value:
        Returns { dms }, list of DM dictionaries for authorised users
    '''
    
    store = data_store.get()
    member_of_dm_list = {
        'dms': []
    }
    for dm in store['dms']:
        for members in dm['all_members']:
            if members['user_id'] == auth_user_id:
                member_of_dm_list['dms'].append({
                    'dm_id': dm['dm_id'],
                    'name': dm['name'],
                })
    
    return member_of_dm_list


def dm_remove(user, dm_id):
    '''
    Removes an existing DM that the user is a creator of.

    Arguments:
        user            dict    - User who is making request
        dm_id           int     - Dm ID of the dm requested for removal

    Exceptions:
        InputError  - Occurs when dm_id is invalid
        AccessError - Occurs when dm_id is valid but either authorised user is not 
                      the original creator or is no longer in the DM

    Return Value:
        Returns {} on successful removal of DM
    '''
    store = data_store.get()

    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            if user in dm['owner_members'] and user in dm['all_members']:
                store['dms'].remove(dm)
                data_store.set(store)
                return {}
            if user in dm['owner_members']:
                raise AccessError(description="Authorised user is no longer in the DM")
            else:
                raise AccessError(description="Authorised user is not the original creator")
    raise InputError(description="DM with dm_id is not valid")

def dm_details(auth_user_id, dm_id):
    
    '''
    Given a DM with ID dm_id that the authorised user is a member of, provides basic details about the DM

    Arguments:
        auth_user_id    int     - User ID of the user who is making the request
        dm_id           int     - Dm ID of the dm requested for details
    
    Exceptions:
        InputError  - Occurs when dm_id is invalid
        AccessError - Occurs when dm_id is valid but user is not a member

    Return Value:
        Returns { name, members },  on valid dm with valid auth user as member
    '''

    store = data_store.get()

    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            for user in dm['all_members']:
                if user['user_id'] == auth_user_id:
                    members = omit_irrelevant_keys(dm, "all_members")
                    return {
                        'name': dm['name'],
                        'members': members
                    }
            raise AccessError(description="Authorised user is not a member")
    
    raise InputError(description="Invalid dm_id")

def dm_leave(auth_user_id, dm_id):
    '''
    Given a dm with ID dm_id that the given user is a member of, 
    remove them as a member of the dm. 
    
    Arguments:
        auth_user_id    int     - User ID of user who is making request
        dm_id           int     - Dm ID of dm requested

    Exceptions:
        Input Error     - Occurs when dm_id does not refer to a valid dm
        Access Error    - Occurs when dm_id is valid but authorised user is not a member of the dm

    Return Value: 
        Returns {} on success
    '''
    store = data_store.get()
    auth_user = check_valid_id(auth_user_id, store)
    dm = get_dm(dm_id, store)
    if not dm:
        raise InputError(description="Invalid DM")

    if not user_in_dm(dm, auth_user_id):
        raise AccessError(description="User is not a member of the DM")
    
    dm['all_members'].remove(auth_user)
    data_store.set(store)
    return {}

def user_in_dm(dm, auth_user_id):
    '''
    Given a dm and a particular user_id returns if user is a member of the dm

    Arguments:
        auth_user_id    int     - User ID of user who is making request
        dm              dict    - Dictionary of a particular dm and its details

    Exceptions:
        N/A

    Return Value: 
        Returns True if user is a member of the dm
        Returns False if user is not a member of the dm
    '''
    for user in dm["all_members"]:
        if auth_user_id == user["user_id"]:
            return True
    return False

def dm_messages(auth_user_id, dm_id, start):
    '''
    Given a dm with ID dm_id that the given user is a member of, 
    return up to 50 messages between index "start" and "start + 50". 
    
    Arguments:
        auth_user_id    int     - User ID of user who is making request
        dm_id      int     - Channel ID of dm requested for details
        start           int     - Index of the newest message to be returned

    Exceptions:
        Input Error     - Occurs when dm_id does not refer to a valid dm
                        - Occurs when start is greater than the total number of messages in the dm
        Access Error    - Occurs when dm_id is valid but authorised user is not a member of the dm
                        - Occurs when auth_user_id passed in is invalid

    Return Value: 
        Returns { messages } as a list of dictionaries, where each dictionary contains types { message_id, u_id, message, time_sent }
        Returns start (Starting index that user gave)
        Returns end index as start + 50, or -1 if it also returns the least recent messages, as an indication there are no more messages to return
    '''
    store = data_store.get()
    dm = get_dm(dm_id, store)
    if not dm:
        raise InputError(description="Invalid DM")

    if not user_in_dm(dm, auth_user_id):
        raise AccessError(description="User is not a member of the dm")

    final_msg = len(dm["messages"])
    if final_msg < start:
        raise InputError(description="Start greater than total number of messages in dm")

    end = start + 50 if (start + 50 < final_msg) else final_msg

    message_list = []
    for message in dm["messages"][start:end]:
        message_list.append({
            "message_id" : message["message_id"],
            "u_id" : message["user_id"],
            "message" : message["message"],
            "time_sent" : message["time_sent"],
        })
    return {"messages" : message_list, "start" : start, "end" : end if (end == start + 50) else -1}




def message_senddm(auth_user_id, dm_id, message):
    '''
    Send a message from authorised user to dm with dm_id.
    
    Arguments:
        auth_user_id    int     - User ID of user who is making request
        dm_id           int     - Dm ID of dm requested
        message         str     - Content of message

    Exceptions:
        Input Error     - Occurs when dm_id does not refer to a valid dm
                        - Occurs when length of message is less than 1 or over 1000 characters
        Access Error    - Occurs when dm_id is valid but authorised user is not a member of the dm

    Return Value: 
        Returns { message_id } on success
    '''
    store = data_store.get()

    dm = get_dm(dm_id, store)
    if not dm:
        raise InputError(description="Invalid Dm")
    
    if not user_in_dm(dm, auth_user_id):
        raise AccessError(description="User is not a member of the Dm")

    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="Length of message is less than 1 or over 1000 characters")

    new_id = store['message_count']
    store['message_count'] += 1
    dm["messages"].insert(
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
    
    
