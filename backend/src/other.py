from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['dms'] = []
    store['dm_count'] = 0
    store['message_count'] = 0
    data_store.set(store)
