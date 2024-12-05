from typing import Optional
from datetime import datetime, timezone, timedelta

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import url_for
import secrets

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
    token: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(32), index=True, unique=True)
    token_expiration: so.Mapped[Optional[datetime]]

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

    def get_token(self, expires_in=3600):
        """
        Generate a token for the user that expires in `expires_in` seconds.
        If a valid token already exists, return it.

        Args:
            expires_in (int): Token expiration time in seconds.

        Returns:
            str: The authentication token.
        """
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration.replace(
                tzinfo=timezone.utc) > now + timedelta(seconds=60):
            return self.token
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        """
        Revoke the user's token manually expiring it.
        """
        self.token_expiration = datetime.now(timezone.utc) - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = db.session.scalar(sa.select(User).where(User.token == token))
        if user is None or user.token_expiration.replace(
                tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return None
        return user

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