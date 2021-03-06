import falcon
import json
import jwt
import bcrypt
from datetime import datetime, timedelta
from app import db
from app.models.users_model import UserModel
from pymongo.errors import DuplicateKeyError
from mongoengine import NotUniqueError 

class Register(object):

    def on_post(self, req, resp):
        username = req.media['username']
        password = req.media['password']
        email = req.media['email']
        fName = req.media['firstName']
        lName = req.media['lastName']

        hashedPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        userObj = UserModel(username=username, password=hashedPassword, email=email, first_name=fName, last_name=lName)
        
        hasError = False
        error = ''

        try:
            userObj.save()
        except (DuplicateKeyError) as err:
            hasError = True
        except (NotUniqueError) as err:
            hasError = True
            if email in err.message:
                error = 'Email already exists'
            if username in err.message:
                error = 'Username already exists'

        if hasError:
            resp.media = {
                'status': 'fail',
                'error': error
            }
        else:
            resp.media = {
                'status': 'successful'
            }
        
class Login(object):

    def on_post(self, req, resp):
        username = req.media['username']
        password = req.media['password']

        user = UserModel.objects(username = username)
        response = {}

        if len(user) > 0:
            user = user[0]
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                response['user'] = str(user.id)
                response['exp'] = datetime.utcnow() + timedelta(seconds=1800)

                jwt_token = jwt.encode(response, 'secret','HS256')
                resp.media = {'token': jwt_token.decode('utf-8')}

            else:
                response['message'] = 'Wrong Passowrd'   
                resp.media = response
        else:
            response['message'] = 'Wrong Username'  
            resp.media = response
        
class ListUsers(object):

    def on_get(self, req, resp):
        
        users = {'users': []}
        
        for user in UserModel.objects:
            user = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'password': user.password,
                'email': user.email
            }
            users['users'].append(user)

        resp.media = users

class SearchUser(object):
    
    def on_get(self, req, resp):
        
        fName = req.media['firstName']
        lName = req.media['lastName']
        potentialUsers = {'potentialUsers': []}

        i = 0

        for user in UserModel.objects:
            if fName == user['first_name'] and lName == user['last_name']:
                user = {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username
                }
                potentialUsers['potentialUsers'].append(user)

        resp.media = potentialUsers 



class Home(object):
    def on_get(self, req, resp):
        resp.media = {'Redirected': True, 'User': req.user}

#LOGIN
#CLIENT SEND REQUEST TO SERVER
#SERVER AUTHS USERNAME AND PASSWORD - SEND BACK JWT
#ONCE SERVER RESPONDS, SAVE JWT INTO COOKIES
