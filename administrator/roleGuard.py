from flask_jwt_extended import get_jwt, verify_jwt_in_request
from functools import wraps
from flask import Response, jsonify
from datetime import datetime

# decorator to allow only target_role to acces a function
def roleGuard(target_role):
    def decorator(function):
        @wraps(function)
        def wrapper(*arguments, **keywordArguments):
            verify_jwt_in_request()
            claims = get_jwt()
            if ("role" in claims) and (claims["role"] == target_role):
                return function(*arguments, **keywordArguments)
            else:
                return jsonify(msg="Missing Authorization Header"),401
        return wrapper
    return decorator