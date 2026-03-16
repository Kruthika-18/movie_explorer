"""
app/models.py - Database Models
---------------------------------
Defines all database tables using SQLAlchemy ORM.
Each class = one table in the database.

SQL Schema Overview:
--------------------
users          - Stores user accounts
watchlist      - Movies/shows a user wants to watch
favorites      - Movies/shows a user loves
watch_history  - Movies/shows a user has watched
reviews        - User ratings and comments
collections    - Custom lists created by users
collection_items - Items inside a collection
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


# ─────────────────────────────────────────────
# USER MODEL
# ─────────────────────────────────────────────
class User(UserMixin, db.Model):
    """
    Stores user account information.
    UserMixin adds is_authenticated, is_active, etc. for Flask-Login.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships (lazy='dynamic' = doesn't load all at once)
    watchlist = db.relationship('Watchlist', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    watch_history = db.relationship('WatchHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    collections = db.relationship('Collection', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and store password. Never store plain text passwords!"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


# Flask-Login needs this to reload user from session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─────────────────────────────────────────────
# WATCHLIST MODEL
# ─────────────────────────────────────────────
class Watchlist(db.Model):
    """Movies/shows a user wants to watch later."""
    __tablename__ = 'watchlist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    imdb_id = db.Column(db.String(20), nullable=False)   # e.g., "tt1234567"
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.String(10))
    poster = db.Column(db.String(500))
    media_type = db.Column(db.String(20))                # 'movie' or 'series'
    genre = db.Column(db.String(200))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Prevent duplicate entries
    __table_args__ = (db.UniqueConstraint('user_id', 'imdb_id'),)


# ─────────────────────────────────────────────
# FAVORITES MODEL
# ─────────────────────────────────────────────
class Favorite(db.Model):
    """Movies/shows a user has marked as favorite."""
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    imdb_id = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.String(10))
    poster = db.Column(db.String(500))
    media_type = db.Column(db.String(20))
    genre = db.Column(db.String(200))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'imdb_id'),)


# ─────────────────────────────────────────────
# WATCH HISTORY MODEL
# ─────────────────────────────────────────────
class WatchHistory(db.Model):
    """Tracks what a user has already watched."""
    __tablename__ = 'watch_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    imdb_id = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.String(10))
    poster = db.Column(db.String(500))
    media_type = db.Column(db.String(20))
    genre = db.Column(db.String(200))
    watched_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────
# REVIEW MODEL
# ─────────────────────────────────────────────
class Review(db.Model):
    """User ratings (1-5 stars) and text reviews."""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    imdb_id = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Integer, nullable=False)   # 1 to 5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # One review per user per movie
    __table_args__ = (db.UniqueConstraint('user_id', 'imdb_id'),)


# ─────────────────────────────────────────────
# COLLECTION MODELS
# ─────────────────────────────────────────────
class Collection(db.Model):
    """User-created custom lists (e.g., 'Date Night Movies')."""
    __tablename__ = 'collections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('CollectionItem', backref='collection', lazy='dynamic', cascade='all, delete-orphan')


class CollectionItem(db.Model):
    """Individual items inside a collection."""
    __tablename__ = 'collection_items'
    
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=False)
    imdb_id = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    poster = db.Column(db.String(500))
    media_type = db.Column(db.String(20))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
