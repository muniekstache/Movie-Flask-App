from flask import request, url_for, abort
from app.api import bp
from app.models import Movie
from app import db
from app.api.errors import bad_request
from app.api.auth import token_auth


@bp.route('/movies', methods=['GET'])
@token_auth.login_required
def get_movies():
    """
    Retrieve all movies.

    Returns:
        dict: A dictionary containing a list of movies and related links.
    """
    movies = Movie.query.all()
    data = {
        'movies': [movie.to_dict() for movie in movies],
        '_links': {
            'self': url_for('api.get_movies', _external=True),
        }
    }
    return data, 200


@bp.route('/movies/<int:id>', methods=['GET'])
@token_auth.login_required
def get_movie(id):
    """
    Retrieve a specific movie by ID.

    Args:
        id (int): The ID of the movie to retrieve.

    Returns:
        dict: A dictionary containing movie details.
    """
    movie = Movie.query.get_or_404(id)
    return movie.to_dict(), 200


@bp.route('/movies', methods=['POST'])
@token_auth.login_required
def create_movie():
    """
    Create a new movie.

    Request Body:
        dict: Must include 'name', 'year', and 'oscars' fields.

    Returns:
        dict: A dictionary containing the created movie's details.
    """
    data = request.get_json() or {}
    # Validate required fields
    required_fields = ['name', 'year', 'oscars']
    for field in required_fields:
        if field not in data:
            return bad_request(f'Must include {field} field')

    # Create new movie
    movie = Movie()
    movie.from_dict(data)
    # Associate the movie with the authenticated user
    movie.user_id = token_auth.current_user().id
    db.session.add(movie)
    db.session.commit()

    response = movie.to_dict()
    response_status = 201
    response_headers = {'Location': url_for('api.get_movie', id=movie.id, _external=True)}
    return response, response_status, response_headers


@bp.route('/movies/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_movie(id):
    """
    Update an existing movie.

    Args:
        id (int): The ID of the movie to update.

    Request Body:
        dict: Fields to update (e.g., 'name', 'year', 'oscars').

    Returns:
        dict: A dictionary containing the updated movie's details.
    """
    movie = Movie.query.get_or_404(id)
    # Ensure that only the owner can update the movie
    if movie.user_id != token_auth.current_user().id:
        abort(403)  # Forbidden
    data = request.get_json() or {}

    # Update movie
    movie.from_dict(data)
    db.session.commit()

    return movie.to_dict(), 200


@bp.route('/movies/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_movie(id):
    """
    Delete a movie.

    Args:
        id (int): The ID of the movie to delete.

    Returns:
        tuple: An empty tuple with a 204 No Content status code.
    """
    movie = Movie.query.get_or_404(id)
    # Ensure that only the owner can delete the movie
    if movie.user_id != token_auth.current_user().id:
        abort(403)  # Forbidden
    db.session.delete(movie)
    db.session.commit()
    return {}, 204
