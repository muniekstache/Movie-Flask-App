from typing import Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
import sqlalchemy.orm as so

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

@login.user_loader
def load_user(id):
    return User.query.get(int(id))