# models.py
from datetime import datetime, timezone
from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    synced_at = db.Column(db.DateTime, nullable=True)
    movies = db.relationship("UserMovie", back_populates="user")


class Movie(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    users = db.relationship("UserMovie", back_populates="movie")


class UserMovie(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    movie_id = db.Column(db.String(255), db.ForeignKey("movie.id"), primary_key=True)
    added_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship("User", back_populates="movies")
    movie = db.relationship("Movie", back_populates="users")
