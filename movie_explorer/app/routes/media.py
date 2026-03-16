"""
app/routes/media.py - Media Detail Routes
------------------------------------------
Handles individual movie/series detail pages,
including recommendations, reviews display.
"""

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user
from app.services.omdb import OMDbService
from app.models import Review, Watchlist, Favorite, WatchHistory

media_bp = Blueprint('media', __name__)


@media_bp.route('/detail/<imdb_id>')
def detail(imdb_id):
    """
    Detailed view for a single movie or series.
    URL example: /media/detail/tt0111161
    """
    try:
        omdb = OMDbService()
        media = omdb.get_details(imdb_id)
        
        if not media:
            flash('Media not found. It may have been removed from the database.', 'warning')
            return redirect(url_for('main.index'))
        
        # Get genre-based recommendations
        genre = media.get('Genre', 'Drama')
        recommendations = omdb.get_recommendations(genre, exclude_id=imdb_id)
        
        # Get all reviews for this media from our database
        reviews = Review.query.filter_by(imdb_id=imdb_id)\
                              .order_by(Review.created_at.desc())\
                              .all()
        
        # Calculate average rating
        avg_rating = 0
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
        
        # Check if current user has this in their lists
        user_lists = {
            'in_watchlist': False,
            'in_favorites': False,
            'in_history': False,
            'user_review': None,
        }
        
        if current_user.is_authenticated:
            user_lists['in_watchlist'] = bool(
                Watchlist.query.filter_by(user_id=current_user.id, imdb_id=imdb_id).first()
            )
            user_lists['in_favorites'] = bool(
                Favorite.query.filter_by(user_id=current_user.id, imdb_id=imdb_id).first()
            )
            user_lists['in_history'] = bool(
                WatchHistory.query.filter_by(user_id=current_user.id, imdb_id=imdb_id).first()
            )
            user_lists['user_review'] = Review.query.filter_by(
                user_id=current_user.id, imdb_id=imdb_id
            ).first()
        
        return render_template(
            'media/detail.html',
            media=media,
            recommendations=recommendations,
            reviews=reviews,
            avg_rating=round(avg_rating, 1),
            review_count=len(reviews),
            **user_lists
        )
        
    except Exception as e:
        flash(f'Error loading media details: {str(e)}', 'danger')
        return redirect(url_for('main.index'))
