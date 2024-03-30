from src.data_store import data_store
from src.error import InputError
from src.auth import check_valid_name, check_valid_email, check_email_registered

def users_all_implement():
    '''
    Returns a list of all users and their associated details.
    There associated details include user_id, email, first name, last name, and handle.

    Arguments:
        N/A

    Exceptions:
        N/A

    Return Value:
        Returns a user dictionary containing the above information. 
    '''
    store = data_store.get()
    user_profile_list = {
        'users': []
    }

    for user in store['users']:
        if not user['is_active']:
            continue
        user_profile_list['users'].append({
            'u_id': user['user_id'],
            'email': user['email'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'handle_str': user['user_handle'],
        }) 

    return user_profile_list


def check_valid_id(auth_user_id, store):
    '''
    Hellper function for user_profile_implement.
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
        if user['user_id'] == auth_user_id:
            return user

    return {}

def user_profile_implement(user_id):
    '''
    Given a valid user, returns information about their user_id, 
        email, first name, last name, and handle

    Arguments:
        user_id            int        - User ID of the user whos profile will be shown

    Exceptions:
        InputError  - Occurs when u_id does not refer to a valid user

    Return Value:
        Returns a user dictionary containing the above information on the condition the user_id is valid. 
    '''
    store = data_store.get()
    user = check_valid_id(user_id, store)
    if not user:
        raise InputError(description='Invalid user_id')

    user_profile = {
        'user': {
            'u_id': user_id,
            'email': user['email'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'handle_str': user['user_handle'],
        },    
    }
    return user_profile

def user_profile_setname_implement(user, name_first, name_last):
    '''
    Given a user, updates their name to the requested name

    Arguments:
        user            dict        - user dict from datastore of given user
        name_first      str         - requested first name
        name_last       str         - requested last name

    Exceptions:
        N/A (handled in helper functions)

    Return Value:
        N/A
    '''
    check_valid_name(name_first)
    check_valid_name(name_last)
    
    user["name_first"] = name_first
    user["name_last"] = name_last
    
def user_profile_setemail_implement(user, email):
    '''
    Given a user, updates their name to the requested name

    Arguments:
        user            dict        - user dict from datastore of given user
        email           str         - requested email

    Exceptions:
        InputError  - Occurs when email is already registered within the system
        
    Return Value:
        N/A
    '''
    check_valid_email(email)
    if check_email_registered(email, data_store.get()):
        raise InputError(description="Email already registered")
    
    user["email"] = email

def user_profile_sethandle_implement(user, handle_str):
    '''
    Given a user, updates their handle to the requested handle

    Arguments:
        user            dict        - user dict from datastore of given user
        handle_str      str         - requested handle

    Exceptions:
        InputError  - Occurs handle is not within 3-20 characters inclusive
                    - Handle contains non-alphanumeric characters
                    - Handle is already in use

    Return Value:
        N/A
    '''
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError(description="Invalid handle, must be within 3-20 characters (inclusive)")
    if not handle_str.isalnum():
        raise InputError(description="Invalid handle, can only contain alphanumeric characters")

    store = data_store.get()
    for users in store["users"]:
        if users["user_handle"] == handle_str:
            raise InputError(description="Handle is already being used by another user")
    
    user["user_handle"] = handle_str