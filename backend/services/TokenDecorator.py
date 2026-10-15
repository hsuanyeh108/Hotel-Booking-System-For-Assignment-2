#JWT Authentication Service and  Decorator
#Design Pattern: Decorator Pattern, add a Layer of Protection to the original function, like the checker(To not change the original function situation)
#Using Class (LoginDecorator and TokenDecorator), store to view function(_call_), for this object to call

#AuthticationTokenService:Generates and decrypts JWT tokens
#TokenDecorator:To protect the Admin API routes: By Checking JWT token, provided in Authorization(Bearer) header

import os #SECRET_KEY environment variable need sign and verify token, can not public
import functools #Let decorator keep the original Flask view function name, document and information
import jwt #Use PyJWT to generate and verify token

from datetime import datetime, timedelta, timezone #need to import datetime, token cannot be effective after 24 hours
from flask import request, jsonify #To read the user HTTP request, return HTTP response as Json in Python
from models.AdminManager import admin_manager #import admin manage object, check whether the account exists

class AuthticationTokenService: #Generates and decrypts JWT tokens
    @staticmethod #no need self, can directly call
    def generate_token(admin_id):
        payload={ #put token data, whose token and expiration time
            "admin_id": admin_id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=24), #using now utc time + 24 hours
        }

        secret_key = os.getenv("SECRET_KEY", "dev-secret-key") #read secret key
        if not secret_key: #if no setting, throw error, avoid empty secret key sign out unsafe token
            raise RuntimeError("SECRET_KEY is not configured")

        return jwt.encode(payload, secret_key, algorithm="HS256")
        #Use HS256 algorithm to sign secret key and return token string

    @staticmethod
    def decode_token(token): #To get secret key, decrypt it and verify token effectiveness,success then payload
        secret_key = os.getenv("SECRET_KEY")    
        if not secret_key:
            raise RuntimeError("SECRET_KEY is not configured")
            #if failed, will throw error(Expired Signature Error or Invalid Token Error)
        return jwt.decode(token, secret_key, algorithms=["HS256"])
        #Use HS256 algorithm to avoid attacker use other algorithm to sign token

class TokenDecorator: #Protect the Admin API routes that require a valid JWT token
    def __init__(self, view_func): #initialize
        self.view_func = view_func
        functools.update_wrapper(self, view_func)
        #copy view_func name, document, information
        #If no copy, the routes of the original function will display endpoint duplicate error

    #_call_ object can call, each request will run here
    # *args, **kwds: let the parameter in routes can paste in    
    def __call__(self, *args, **kwds): #To check and decrypt Authorization JWT, if verify success save admin in request.current_admin
        auth_header = request.headers.get("Authorization", "")
        #read the Authorization header request, if no then use empty string

        if not auth_header.startswith("Bearer"):
            return jsonify({"message": "Missing or invalid Authorization header"}), 401
            #Standard format: Authorization: Bearer <token>, if not return 401(no Authorization)

        token = auth_header.split("", 1)[1]
        #First space split, [1] is afer Bearer's token
            
        try:
            payload = AuthticationTokenService.decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        #try decrypt token, expired return Token expired, other error return Invalid token, both 401

        admin = admin_manager.get_by_id(payload.get("admin_id"))
        if not admin:
            return jsonify({"message": "Admin not found"}), 401
        #Not only token is effective, but also need to check whether the account exists in the database
        #ex: account is deleted, the old token should not still be effective

        request.current_admin = admin
        #put the admin data on the request, let the routes can use request.current_admin to know who are operating

        return self.view_func(*args, **kwds)
        #All pass, then real run the route
