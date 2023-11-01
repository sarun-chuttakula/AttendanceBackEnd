from functools import wraps
import jwt
from flask import request, abort, current_app
import services as services
from datetime import datetime, timedelta


def generate_access_token(user_id,user_email):
    # Generate a new access token with a 24-hour expiration time
    expiration = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "id": user_id,
        "email": user_email,
        "exp": expiration,
    }
    access_token = jwt.encode(
        payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")
    return access_token


def jwttoken_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
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
            data = jwt.decode(
                token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
            current_user = services.User().get_user_by_id(data["id"])
            if current_user is None:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401
            if not current_user["active"]:
                abort(403)
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated


def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return {
                    "message": "Authentication Token is missing!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401
            try:
                data = jwt.decode(token.split(
                    " ")[1], current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
                role = data.get("role")
                if role in allowed_roles:
                    return f(current_user, *args, **kwargs)
                else:
                    return {
                        "message": "Unauthorized",
                        "error": "You do not have permission to access this resource",
                        "data": None
                    }, 403
            except Exception as e:
                return {
                    "message": "Something went wrong",
                    "data": None,
                    "error": str(e)
                }, 500
        return decorated_function
    return decorator
