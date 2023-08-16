import pickle

# Save the dictionary to a file
def save_dict(dict, filename):
    with open(filename, 'wb') as file:
        pickle.dump(dict, file)

# Load the dictionary from a file
def load_dict(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)
    
def clear_users(filename):
    new_users = {}
    save_dict(new_users, filename)

def remove_user(username, filename):
    users = load_dict(filename)
    if username in users:
        del users[username]
    save_dict(users, filename)