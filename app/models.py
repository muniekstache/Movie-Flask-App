from typing import Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import url_for

from app import db, login


# User model representing the users table
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    movies: so.Mapped[list['Movie']] = so.relationship('Movie', back_populates='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_email=False):
        """
        Serializes the User instance to a dictionary.

        Args:
            include_email (bool): If True, includes the user's email in the output.

        Returns:
            dict: A dictionary representation of the user.
        """
        data = {
            'id': self.id,
            'username': self.username,
            'movies_count': self.movies.count(),
            '_links': {
                'self': url_for('api.get_user', id=self.id, _external=True),
                'movies': url_for('api.get_user_movies', id=self.id, _external=True)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        """
        Deserializes a dictionary to update the User instance.

        Args:
            data (dict): A dictionary containing user data.
            new_user (bool): If True, expects a 'password' field to set the password.
        """
        for field in ['username', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def __repr__(self):
        return f'<User {self.username}>'


# Movie model representing the movies table
class Movie(db.Model):
    __tablename__ = 'movie'
    __table_args__ = {'extend_existing': True}
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    year: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    oscars: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    user: so.Mapped['User'] = so.relationship('User', back_populates='movies')

    def to_dict(self):
        """
        Serializes the Movie instance to a dictionary.

        Returns:
            dict: A dictionary representation of the movie.
        """
        data = {
            'id': self.id,
            'name': self.name,
            'year': self.year,
            'oscars': self.oscars,
            'user_id': self.user_id,
            '_links': {
                'self': url_for('api.get_movie', id=self.id, _external=True),
                'user': url_for('api.get_user', id=self.user_id, _external=True)
            }
        }
        return data

    def from_dict(self, data):
        """
        Deserializes a dictionary to update the Movie instance.

        Args:
            data (dict): A dictionary containing movie data.
        """
        for field in ['name', 'year', 'oscars']:
            if field in data:
                setattr(self, field, data[field])

@login.user_loader
def load_user(id):
    return User.query.get(int(id))