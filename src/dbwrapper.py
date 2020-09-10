import os
import sys
import pymongo
from dotenv import load_dotenv
from bson.codec_options import CodecOptions
import pytz
from datetime import datetime


class Database:
    def __init__(self, connection_string, is_production=False):
        client = pymongo.MongoClient(connection_string)
        self.db = client['approxima']

        self.users = self.db['production-users'] if is_production else self.db['users']
        self.users = self.users.with_options(codec_options=CodecOptions(
            tz_aware=True,
            tzinfo=pytz.timezone('America/Sao_Paulo')))

        self.stats = self.db['production-stats'] if is_production else self.db['test-stats']
        self.stats = self.stats.with_options(codec_options=CodecOptions(
            tz_aware=True,
            tzinfo=pytz.timezone('America/Sao_Paulo')))

        self.today_id = self.__create_today_id()
        self.__create_today_doc()
        self.users_doc_checked = {}  # Map from a user_id to a boolean

    def __create_today_id(self):
        today_date = datetime.utcnow()
        today_id = f"{today_date.year}-{today_date.month}-{today_date.day}"
        return today_id

    def __create_today_user_doc(self, user_id):
        try:
            self.stats.update_one({'_id': self.today_id}, {
                                  "$push": {"active_users": {"_id": user_id}}})
        except:
            print(
                f"An exception occurred in the database while creating the user doc for day {datetime.utcnow()}:\n")
            print(sys.exc_info()[0])

    def __create_today_doc(self):
        try:
            self.stats.insert_one(
                {"_id": self.today_id, "active_users": []})
        except:
            print(
                f"An exception occurred in the database while creating the {self.today_id} day doc:\n")
            print(sys.exc_info()[0])

    def list_user_ids(self):
        ids = []
        for user in self.users.find():
            ids.append(user['_id'])
        return ids

    def list_chat_ids(self):
        chat_ids = []
        for user in self.users.find():
            chat_ids.append(user['chat_id'])
        return chat_ids

    def get_user_by_id(self, telegram_id):
        try:
            return self.users.find_one({'_id': telegram_id})
        except:
            print("An exception occurred in the database while getting user by id:\n")
            print(sys.exc_info()[0])

    def get_users_in_list(self, users_list):
        # Users list is a list of telegram ID's
        try:
            query = {"_id": {"$in": users_list}}
            response = self.users.find(query)
            return list(response)
        except:
            print(
                "An exception occurred in the database while getting users in a list:\n")
            print(sys.exc_info()[0])

    def update_user_by_id(self, telegram_id, data):
        try:
            new_values = {"$set": data}
            new_values["$set"]["updated_at"] = datetime.utcnow()
            self.users.update_one({'_id': telegram_id}, new_values)
        except:
            print("An exception occurred in the database while updating user by id:\n")
            print(sys.exc_info()[0])

    def insert_user(self, telegram_id, data):
        try:
            new_document = {
                "_id": telegram_id,
                "chat_id": data['chat_id'],
                "username": data['username'],
                "name": data['name'],
                "bio": data['bio'],
                "interests": data['interests'],
                "rejects": data['rejects'],
                "invited": data['invited'],
                "pending": data['pending'],
                "connections": data['connections'],
                "created_at": datetime.utcnow(),
                "updated_at": None,
            }
            self.users.insert_one(new_document)
        except:
            print("An exception occurred in the database while updating user by id:\n")
            print(sys.exc_info()[0])

    def register_action(self, action_name, user_id, additional_data=None):
        if not user_id or not action_name:
            raise ValueError(
                "Both \"action_name\" and \"user_id\" are required.")

        # Additional data must be a dict if not none
        if additional_data is not None and not isinstance(additional_data, dict):
            raise ValueError("\"additional_data\" must be a dict.")

        # Make sure that everything is ok with the Database before proceeding
        tid = self.__create_today_id()
        if tid != self.today_id:
            # I am in another day!
            self.today_id = tid
            self.__create_today_doc()
            self.__create_today_user_doc(user_id)
            self.user_doc_checked = True
        else:
            # Se não existir a entrada para este usuario OU se o booleano for False...
            if not self.users_doc_checked.get(user_id):
                # I'm gonna check it!
                query = {'_id': self.today_id, "active_users._id": user_id}
                if not self.stats.find_one(query):
                    self.__create_today_user_doc(user_id)
                    self.users_doc_checked[user_id] = True

        action = {}
        action['timestamp'] = datetime.utcnow()

        if additional_data:
            action['data'] = additional_data

        try:
            # Push to the correct array
            query = {'_id': self.today_id, "active_users._id": user_id}
            update = {"$push": {f"active_users.$.{action_name}": action}}

            self.stats.update_one(query, update)

        except:
            print(
                f"An exception occurred in the database while adding an action to user {user_id}:\n")
            print(sys.exc_info()[0])


def test():
    load_dotenv()
    CONNECTION_STRING = os.getenv("CONNECTION_STRING")
    db = Database(CONNECTION_STRING)


if __name__ == '__main__':
    test()
