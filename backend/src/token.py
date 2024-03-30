import jwt
from src.data_store import data_store
from src.error import AccessError

SECRET = "far_plants"

def encode(data):
    '''
    Creates a jwt (token) for a particular user given some data

    Arguments:
        data       dict     - {user_id, session}

    Exceptions:
        N/A

    Return Value:
        Returns JWT token
    '''
    return jwt.encode(data, SECRET, algorithm="HS256")

def decode(token):
    '''
    Given a token, decodes the data

    Arguments:
        token       str     - JWT token

    Exceptions:
        Access Error        - In line with section 6.3, an invalid token raises an access error

    Return Value:
        Returns {user_id, session} on condition that no errors occurred during decoding
    '''
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except Exception as decode_error:
        raise AccessError(description='Invalid token') from decode_error

def check_valid_token(user_data):
    '''
    Given user data from a token, checks if the token data was valid
        i.e. the user exists and the session exists for that user

    Arguments:
        token       dict    -  {user_id, session}

    Exceptions:
        N/A

    Return Value:
        Returns user on condition that the user's id exists and session is valid
        Returns {} if no user was found or session is invalid
    '''
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == user_data['user_id'] and user_data['session'] in user['sessions']:
            return user

    return {}
