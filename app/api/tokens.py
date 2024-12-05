from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth


@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    """
    Obtain an authentication token by providing valid Basic Auth credentials.

    Returns:
        dict: A dictionary containing the authentication token.
    """
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return {'token': token}, 200


@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    """
    Revoke the current user's authentication token.

    Returns:
        Response: Empty response with 204 No Content status code.
    """
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204