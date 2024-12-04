from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException
from app.api import bp


def error_response(status_code, message=None):
    """
    Generates a JSON error response.

    Args:
        status_code (int): HTTP status code.
        message (str, optional): Detailed error message.

    Returns:
        Response: Flask JSON response with error details.
    """
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = payload
    response.status_code = status_code
    return response


def bad_request(message):
    """
    Generates a 400 Bad Request error response.

    Args:
        message (str): Detailed error message.

    Returns:
        Response: Flask JSON response with 400 status code.
    """
    return error_response(400, message)

@bp.errorhandler(HTTPException)
def handle_http_exception(e):
    """
    Handles all HTTP exceptions and returns JSON responses.

    Args:
        e (HTTPException): The exception that was raised.

    Returns:
        Response: Flask JSON response with error details.
    """
    return error_response(e.code, e.description)