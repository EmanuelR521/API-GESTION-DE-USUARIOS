from flask import Flask, jsonify, request
import json
import pymongo
from user import User
from userHandler import UserHandler
from login import Login
from loginHandler import LoginHandler
import bcrypt
from functools import wraps
import tokenMiddleware
from config import Config

conf = Config()


test = Flask(__name__) 


uri = conf.uri


dbname = conf.db_name

mongoClient = pymongo.MongoClient(uri)

def login_required(f):
    
    @wraps(f)
    def decorated(*args, **kwargs):
        db = pymongo.MongoClient(uri)["admins"]
        token = request.headers.get('token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = tokenMiddleware.decode_token(token)
            if not data:
                return jsonify({'message': 'Token is invalid or expired!'}), 401
            # Obtener el usuario basado en los datos del token
            current_user = db.admins.find_one({'username': data['username']})
        except Exception as e:
            print(f"Error decoding token: {e}")
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated



@test.route('/v1/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    login = Login(username, password)
    loginHandler = LoginHandler(dbname,uri, mongoClient)
    response = LoginHandler.login(loginHandler,login)
    if response:
        return json.dumps({'message': response}), 200
    else:
        return json.dumps({'message': 'Login failed :( '}), 500
    


@test.route('/v1/createUser', methods=['POST'])  
@login_required     
def userRegister():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    hashedPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    newUser = User(username,email,hashedPassword, None)
    newUserHandler = UserHandler(dbname,uri, mongoClient)
    response = UserHandler.createUser(newUserHandler,newUser)
    if response:
        return json.dumps({'message': 'User created successfully :)'}), 201
    else:
        return json.dumps({'message': 'User not created :( '}), 400
    
@test.route('/v1/getUsers', methods=['GET'])
@login_required     
def getUsers():
    newUserHandler = UserHandler(dbname,uri, mongoClient)
    response = UserHandler.getUsers(newUserHandler)
    users = []  
    for user in response:
        user._id = str(user._id) 
        user.password = str(user.password)
        userJson = user.to_dict()
        userJson['_id'] = user._id
        users.append(userJson) 
    if response is None:
        return json.dumps({'message': 'No users found :('}), 404
    return json.dumps(users), 200

@test.route('/v1/getUser', methods=['GET'])
@login_required     
def getUserByID():
    user_id = request.headers.get('id')
    print(user_id)
    newUserHandler = UserHandler(dbname,uri, mongoClient)
    response = UserHandler.getUser(newUserHandler, user_id)
    print(response)
    if response is None:
        return json.dumps({'message': 'User not found :('}), 404
    else:
        response['_id'] = str(response['_id']) 
        response['password'] = str(response['password'])	
        return jsonify(response), 200
    
@test.route('/v1/updateUser', methods=['PUT'])
@login_required     
def updateUser():
    user_id = request.headers.get('id')
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    hashedPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    newUser = User(username,email, hashedPassword, None)
    newUserHandler = UserHandler(dbname,uri, mongoClient)
    response = UserHandler.updateUser(newUserHandler, user_id, newUser)
    print(response)
    if response['updated_count'] > 0:
        return json.dumps({'message': 'User updated successfully :)'}), 200
    else:
        return json.dumps({'message': 'User not updated :( '}), 400
    
@test.route('/v1/deleteUser', methods=['DELETE'])  
@login_required     
def deleteUser():
    user_id = request.headers.get('id')
    newUserHandler = UserHandler(dbname,uri, mongoClient)
    response = UserHandler.deleteUser(newUserHandler, user_id)
    if response['updated_count'] > 0:
        return json.dumps({'message': 'User deleted successfully :)'}), 204
    else:
        return json.dumps({'message': 'User not deleted :( '}), 404
   


if __name__ == '__main__':
    test.run(debug=True, host='0.0.0.0', port=6969,threaded=False)