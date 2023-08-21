from pymongo import MongoClient

class UserDataManager:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client["UserData"]
        self.collection = self.db["kopiServer"]

        # Create a unique index on the username field
        self.collection.create_index([("username", 1)], unique=True)

    def create_user(self, user_data):
        # Check if the username or email already exists
        existing_user = self.collection.find_one(
            {"$or": [{"username": user_data["username"]}, {"email": user_data["email"]}]})

        if existing_user:
            return False  # User with the same username or email already exists

        try:
            self.collection.insert_one(user_data)
            return True
        except:
            return False


    def remove_user(self, username):
        self.collection.delete_one({"username": username})

    def get_users(self):
        return list(self.collection.find({}, {"username": 1}))
    
    def get_usernames(self):
        users = self.get_users()
        usernames = []
        for user in users:
            usernames.append(user['username'])
        return usernames

    def clear_users(self):
        self.collection.delete_many({})

    def get_user(self, username):
        return self.collection.find_one({"username": username})
    
    def update_user(self, username, update_data):
        return self.collection.update({'username': username}, update_data)

    def add_workspace(self, username, workspace_data):
        result = self.collection.update({'username': username}, {'$push': {'workspaces': workspace_data}})
        return result

    def remove_workspace(self, username, workspace):
        return self.collection.update({'username': username}, {"$pull": {"workspaces": workspace}})

    def add_connected_friend(self, username, friend_username):
        update_data = {"$push": {"friends.connected": friend_username}}
        return self.update_user(username, update_data)

    def add_sent_request(self, username, friend_username):
        update_data = {"$push": {"friends.sent": friend_username}}
        return self.update_user(username, update_data)

    def add_received_request(self, username, friend_username):
        update_data = {"$push": {"friends.received": friend_username}}
        return self.update_user(username, update_data)
    
    def update_bio(self, username, bio):
        update_data = {"$set": {"bio": bio}}
        return self.update_user(username, update_data)
    
    def remove_connected_friend(self, username, friend_username):
        update_data = {"$pull": {"friends.connected": friend_username}}
        return self.update_user(username, update_data)


    def remove_sent_request(self, username, friend_username):
        update_data = {"$pull": {"friends.sent": friend_username}}
        return self.update_user(username, update_data)

    def remove_received_request(self, username, friend_username):
        update_data = {"$pull": {"friends.received": friend_username}}
        return self.update_user(username, update_data)

    def get_workspaces(self, username):
        user = self.get_user(username)
        return user.get("workspaces", [])

    def get_connected_friends(self, username):
        user = self.get_user(username)
        return user.get("friends", {}).get("connected", [])

    def get_sent_friend_requests(self, username):
        user = self.get_user(username)
        return user.get("friends", {}).get("sent", [])

    def get_received_friend_requests(self, username):
        user = self.get_user(username)
        return user.get("friends", {}).get("received", [])
