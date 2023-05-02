from functools import wraps
import jwt
from flask import request
from flask import current_app
import json


clear_text_token = "eyJhbGciOiJIUzI1NiIsInR5c2VYyyBbbMmmFtZSI6Im1sdXVra2FpIiwiaW"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print('Authenticating')
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            decoded_token_json =jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            incoming_token = decoded_token_json['token']
            if incoming_token != clear_text_token:
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        except Exception as e:
            print('EXCEPT',str(e))
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(*args, **kwargs)

    return decorated