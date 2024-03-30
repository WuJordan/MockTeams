import pickle
from src.data_store import data_store

def save_persistence():
    store = data_store.get()
    with open('datastore.p', 'wb') as FILE:
        pickle.dump(store, FILE)