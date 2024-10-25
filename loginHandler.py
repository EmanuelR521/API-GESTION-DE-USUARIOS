from pymongo import MongoClient
from login import Login
from pymongo.server_api import ServerApi
import bcrypt
import tokenMiddleware

class LoginHandler:

    def __init__(self,db_name: str,  uri: str = None, connection: MongoClient = None) -> None:
        if connection is not None:
            self.connection = connection
        else:
            self.connection = MongoClient(uri, server_api=ServerApi('1'))
        self.db_name = db_name

    def login(self,login: Login) -> bool:
        db = self.connection[self.db_name]
        user = db.admins.find_one({'username': login.username})
        password = login.password.encode('utf-8')
        token = tokenMiddleware.generate_token(login.username)
        if bcrypt.checkpw(password, user['password']):
            return token
        else:
            return False