import sqlalchemy as sa
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app import db
from app.models import User
from app.api.errors import error_response

# Initialize authentication handlers
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Bearer')


@basic_auth.verify_password
def verify_password(username, password):
    """
    Verify user credentials for Basic Authentication.

    Args:
        username (str): The username provided by the client.
        password (str): The password provided by the client.

    Returns:
        User or None: Returns the user object if credentials are valid, else None.
    """
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user and user.check_password(password):
        return user


@basic_auth.error_handler
def basic_auth_error(status):
    """
    Handle Basic Authentication errors.

    Args:
        status (int): HTTP status code.

    Returns:
        Response: JSON response with error details.
    """
    return error_response(status)


@token_auth.verify_token
def verify_token(token):
    """
    Verify the provided token for Token Authentication.

    Args:
        token (str): The authentication token provided by the client.

    Returns:
        User or None: Returns the user object if token is valid, else None.
    """
    return User.check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status):
    """
    Handle Token Authentication errors.

    Args:
        status (int): HTTP status code.

    Returns:
        Response: JSON response with error details.
    """
    return error_response(status)