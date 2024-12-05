from flask import request, url_for, abort
from app.api import bp
from app.models import User
from app import db
from app.api.errors import bad_request
from app.api.auth import token_auth


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    """
    Retrieve all users.

    Returns:
        dict: A dictionary containing a list of users and related links.
    """
    users = User.query.all()
    data = {
        'users': [user.to_dict() for user in users],
        '_links': {
            'self': url_for('api.get_users', _external=True),
        }
    }
    return data, 200


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    """
    Retrieve a specific user by ID.

    Args:
        id (int): The ID of the user to retrieve.

    Returns:
        dict: A dictionary containing user details.
    """
    user = User.query.get_or_404(id)
    if user != token_auth.current_user():
        abort(403)  # Forbidden
    return user.to_dict(), 200


@bp.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user.

    Request Body:
        dict: Must include 'username', 'email', and 'password' fields.

    Returns:
        dict: A dictionary containing the created user's details.
    """
    data = request.get_json() or {}
    # Validate required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return bad_request(f'Must include {field} field')

    # Check for existing username and email
    if User.query.filter_by(username=data['username']).first():
        return bad_request('Please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('Please use a different email address')

    # Create new user
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()

    response = user.to_dict(include_email=True)
    response_status = 201
    response_headers = {'Location': url_for('api.get_user', id=user.id, _external=True)}
    return response, response_status, response_headers


@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    """
    Update an existing user.

    Args:
        id (int): The ID of the user to update.

    Request Body:
        dict: Fields to update (e.g., 'username', 'email', 'password').

    Returns:
        dict: A dictionary containing the updated user's details.
    """
    user = User.query.get_or_404(id)
    if user != token_auth.current_user():
        abort(403)  # Forbidden
    data = request.get_json() or {}

    # Check for username and email uniqueness if they are being updated
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return bad_request('Please use a different username')
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return bad_request('Please use a different email address')

    # Update user
    user.from_dict(data, new_user=False)
    db.session.commit()

    return user.to_dict(), 200


@bp.route('/users/<int:id>/movies', methods=['GET'])
@token_auth.login_required
def get_user_movies(id):
    """
    Retrieve all movies associated with a specific user.

    Args:
        id (int): The ID of the user whose movies to retrieve.

    Returns:
        dict: A dictionary containing a list of movies and related links.
    """
    user = User.query.get_or_404(id)
    if user != token_auth.current_user():
        abort(403)  # Forbidden
    movies = user.movies.all()
    data = {
        'movies': [movie.to_dict() for movie in movies],
        '_links': {
            'self': url_for('api.get_user_movies', id=id, _external=True),
            'user': url_for('api.get_user', id=id, _external=True)
        }
    }
    return data, 200