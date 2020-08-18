import os
import sys
import pymongo
from dotenv import load_dotenv


class Database:
    def __init__(self, connection_string, is_production=False):
        client = pymongo.MongoClient(connection_string)
        self.db = client['approxima']
        self.users = self.db['production-users'] if is_production else self.db['users']

    def list_ids(self):
        ids = []
        for user in self.users.find():
            ids.append(user['_id'])
        return ids

    def get_by_id(self, telegramId):
        try:
            return self.users.find_one({'_id': telegramId})
        except:
            print("An exception occurred in the database while getting user by id:\n")
            print(sys.exc_info()[0])

    def update_by_id(self, telegramId, data):
        try:
            new_values = {"$set": data}
            self.users.update_one({'_id': telegramId}, new_values)
        except:
            print("An exception occurred in the database while updating user by id:\n")
            print(sys.exc_info()[0])

    def insert(self, telegramId, data):
        try:
            new_document = {
                "_id": telegramId,
                "chat_id": data['chat_id'],
                "username": data['username'],
                "name": data['name'],
                "bio": data['bio'],
                "interests": data['interests'],
                "rejects": data['rejects'],
                "invited": data['invited'],
                "pending": data['pending'],
                "connections": data['connections']
            }
            self.users.insert_one(new_document)
        except:
            print("An exception occurred in the database while updating user by id:\n")
            print(sys.exc_info()[0])


def test():
    load_dotenv()
    CONNECTION_STRING = os.getenv("CONNECTION_STRING")
    db = Database(CONNECTION_STRING)
    db.list_ids()


if __name__ == '__main__':
    test()
