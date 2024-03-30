from src.data_store import data_store
from src.error import InputError
from src.token import encode
from datetime import datetime
import re

def check_valid_email(email):
    '''
    Checks if the email given is of a valid format as given in the regular expression

    Arguments:
        email       str         - Email given by the user

    Exceptions:
        InputError  - Occurs when the email has an incorrect format

    Return Value:
        N/A
    '''
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.fullmatch(regex, email):
        raise InputError(description="Invalid email")

def check_email_registered(email, store):
    '''
    Checks if the email given is already registered within the system

    Arguments:
        email       str         - Email given by the user
        store       dict        - Database of Seams information

    Exceptions:
        InputError  - Occurs when password is too short

    Return Value:
        Returns user dict on success in finding given user
        Returns empty dict on failure in finding given user
    '''
    for user in store["users"]:
        if user["email"] == email:
            return user
    
    return {}

def check_valid_name(name):
    '''
    Checks if the name given is within the 1-50 (inclusive) character limit

    Arguments:
        name        str         - First name or last name, depending on when the function is called

    Exceptions:
        InputError  - Occurs when name is not within the character limit

    Return Value:
        N/A
    '''
    if len(name) < 1 or len(name) > 50:
        raise InputError(description="Invalid name, must be within 1-50 characters (inclusive)")

def do_create_new_handle(name, new_handle):
    '''
    Helper function for create_new_handle to create the initial string.

    Arguments:
        name        str         - First name or last name, depending on when the function is called
        new_handle  str         - Empty or partially completed string to fill with new_handle

    Exceptions:
        N/A

    Return Value:
        Returns new_handle string with additions
    '''
    for char in name:
        if char.isalnum():
            if not new_handle:
                new_handle = char
            else:
                new_handle = new_handle + char
    return new_handle

def create_new_handle(name_first, name_last, store):
    '''
    Creates a new, unique, handle for each user in Seams that is max 20
    characters in length, unless a number is appended to create uniqueness
    in which case it goes over this limit.

    Arguments:
        name_first  str     - Must be within 1-50 characters inclusive
        name_second str     - Must be within 1-50 characters inclusive

    Exceptions:
        N/A

    Return Value:
        Returns new_handle once created
    '''
    new_handle = ""
    new_handle = do_create_new_handle(name_first, new_handle)
    new_handle = do_create_new_handle(name_last, new_handle)

    if len(new_handle) > 20:
        new_handle = new_handle[0:20]
        
    append_number = 0
    dupe_handle = new_handle
    for user in store["users"]:
        if user["user_handle"] == new_handle:
            new_handle = f"{dupe_handle}{append_number}"
            append_number += 1

    return new_handle

def auth_login_v1(email, password):
    '''
    Logs an existing user onto the Seams database

    Arguments:
        email       str     - Valid email, unique to each user
        password    str     - Password must be >= 6 characters

    Exceptions:
        InputError  - Occurs when password does not match what's in the system

    Return Value:
        Returns auth_user_id on successful login
    '''
    store = data_store.get()
    user = check_email_registered(email, store)
    if not user:
        raise InputError(description="User does not exist")
    if user["password"] != password:
        raise InputError(description="Incorrect password")

    session = datetime.now()
    session = session.strftime("%c")
    user["sessions"].append(session)
    user["total_sessions"] += 1

    return {
        "token" : encode({
            "user_id": user["user_id"], 
            "session" : session, 
            "total_sessions" : user["total_sessions"]}),
        "auth_user_id" : user["user_id"],
    }

def auth_register_v1(email, password, name_first, name_last):
    '''
    Registers a user into the Seams database

    Arguments:
        email       str     - Valid email, unique to each user
        password    str     - Password must be >= 6 characters
        name_first  str     - Must be within 1-50 characters inclusive
        name_second str     - Must be within 1-50 characters inclusive

    Exceptions:
        InputError  - Occurs when email is already registered within the system

    Return Value:
        Returns {token, auth_user_id} on successful registration
    '''
    check_valid_name(name_first)
    check_valid_name(name_last)
    check_valid_email(email)

    store = data_store.get()
    if check_email_registered(email, store):
        raise InputError(description="Email already registered")

    new_id = len(store["users"])
    new_handle = create_new_handle(name_first.lower(), name_last.lower(), store)
    session = datetime.now()
    session = session.strftime("%c")

    store["users"].append({
        "user_id": new_id, 
        "user_handle" : new_handle, 
        "is_owner" : False if new_id else True, # if user_id is 0, i.e. first user that signs up, is owner by default
        "email" : email, 
        "password" : password, 
        "name_first" : name_first, 
        "name_last" : name_last,
        "sessions" : [session], # store datetimes that sessions were created to ensure uniqueness
        "total_sessions" : 1,
        "is_active" : True # switches to false when user is removed from seams
    })
    data_store.set(store)
    return {
        "token" : encode({
            "user_id": new_id, 
            "session" : session, 
            "total_sessions" : 1}),
        "auth_user_id" : new_id,
    }
