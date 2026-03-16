"""
app/routes/user.py - User Feature Routes
-----------------------------------------
Handles all user-specific features:
- Watchlist management
- Favorites management
- Watch history
- Reviews/ratings
- Dashboard statistics
- Custom collections
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from collections import Counter
from app import db
from app.models import Watchlist, Favorite, WatchHistory, Review, Collection, CollectionItem

user_bp = Blueprint('user', __name__)


# ─────────────────────────────────────────────
# WATCHLIST
# ─────────────────────────────────────────────

@user_bp.route('/watchlist')
@login_required
def watchlist():
    """Display user's watchlist."""
    items = current_user.watchlist.order_by(Watchlist.added_at.desc()).all()
    return render_template('user/watchlist.html', items=items)


@user_bp.route('/watchlist/add', methods=['POST'])
@login_required
def add_to_watchlist():
    """Add a movie to watchlist. Expects form data."""
    imdb_id = request.form.get('imdb_id')
    title = request.form.get('title')
    year = request.form.get('year')
    poster = request.form.get('poster')
    media_type = request.form.get('media_type')
    genre = request.form.get('genre', '')
    
    # Check if already in watchlist
    existing = Watchlist.query.filter_by(
        user_id=current_user.id, imdb_id=imdb_id
    ).first()
    
    if existing:
        flash(f'"{title}" is already in your watchlist.', 'info')
    else:
        item = Watchlist(
            user_id=current_user.id,
            imdb_id=imdb_id,
            title=title,
            year=year,
            poster=poster,
            media_type=media_type,
            genre=genre,
        )
        db.session.add(item)
        db.session.commit()
        flash(f'"{title}" added to your watchlist! 📋', 'success')
    
    return redirect(request.referrer or url_for('media.detail', imdb_id=imdb_id))


@user_bp.route('/watchlist/remove/<imdb_id>', methods=['POST'])
@login_required
def remove_from_watchlist(imdb_id):
    """Remove an item from watchlist."""
    item = Watchlist.query.filter_by(
        user_id=current_user.id, imdb_id=imdb_id
    ).first_or_404()
    
    title = item.title
    db.session.delete(item)
    db.session.commit()
    flash(f'"{title}" removed from watchlist.', 'success')
    return redirect(request.referrer or url_for('user.watchlist'))


# ─────────────────────────────────────────────
# FAVORITES
# ─────────────────────────────────────────────

@user_bp.route('/favorites')
@login_required
def favorites():
    """Display user's favorites."""
    items = current_user.favorites.order_by(Favorite.added_at.desc()).all()
    return render_template('user/favorites.html', items=items)


@user_bp.route('/favorites/add', methods=['POST'])
@login_required
def add_to_favorites():
    imdb_id = request.form.get('imdb_id')
    title = request.form.get('title')
    
    existing = Favorite.query.filter_by(
        user_id=current_user.id, imdb_id=imdb_id
    ).first()
    
    if existing:
        flash(f'"{title}" is already in your favorites.', 'info')
    else:
        item = Favorite(
            user_id=current_user.id,
            imdb_id=imdb_id,
            title=title,
            year=request.form.get('year'),
            poster=request.form.get('poster'),
            media_type=request.form.get('media_type'),
            genre=request.form.get('genre', ''),
        )
        db.session.add(item)
        db.session.commit()
        flash(f'"{title}" added to favorites! ❤️', 'success')
    
    return redirect(request.referrer or url_for('media.detail', imdb_id=imdb_id))


@user_bp.route('/favorites/remove/<imdb_id>', methods=['POST'])
@login_required
def remove_from_favorites(imdb_id):
    item = Favorite.query.filter_by(
        user_id=current_user.id, imdb_id=imdb_id
    ).first_or_404()
    
    title = item.title
    db.session.delete(item)
    db.session.commit()
    flash(f'"{title}" removed from favorites.', 'success')
    return redirect(request.referrer or url_for('user.favorites'))


# ─────────────────────────────────────────────
# WATCH HISTORY
# ─────────────────────────────────────────────

@user_bp.route('/history')
@login_required
def history():
    """Display watch history."""
    items = current_user.watch_history.order_by(WatchHistory.watched_at.desc()).all()
    return render_template('user/history.html', items=items)


@user_bp.route('/history/add', methods=['POST'])
@login_required
def add_to_history():
    imdb_id = request.form.get('imdb_id')
    title = request.form.get('title')
    
    # Don't add duplicates - just update timestamp
    existing = WatchHistory.query.filter_by(
        user_id=current_user.id, imdb_id=imdb_id
    ).first()
    
    if not existing:
        item = WatchHistory(
            user_id=current_user.id,
            imdb_id=imdb_id,
            title=title,
            year=request.form.get('year'),
            poster=request.form.get('poster'),
            media_type=request.form.get('media_type'),
            genre=request.form.get('genre', ''),
        )
        db.session.add(item)
        db.session.commit()
        flash(f'"{title}" marked as watched! ✅', 'success')
    else:
        flash(f'"{title}" is already in your watch history.', 'info')
    
    return redirect(request.referrer or url_for('media.detail', imdb_id=imdb_id))


# ─────────────────────────────────────────────
# REVIEWS
# ─────────────────────────────────────────────

@user_bp.route('/review/add', methods=['POST'])
@login_required
def add_review():
    """Submit a rating and review."""
    imdb_id = request.form.get('imdb_id')
    title = request.form.get('title')
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()
    
    if not rating or rating < 1 or rating > 5:
        flash('Please select a valid rating (1-5 stars).', 'danger')
        return redirect(request.referrer)
    
    # Update existing review or create new
    review = Review.query.filter_by(
        user_id=current_user.id, imdb_id=imdb_id
    ).first()
    
    if review:
        review.rating = rating
        review.comment = comment
        flash('Your review has been updated! ✏️', 'success')
    else:
        review = Review(
            user_id=current_user.id,
            imdb_id=imdb_id,
            title=title,
            rating=rating,
            comment=comment,
        )
        db.session.add(review)
        flash('Review submitted! Thank you! ⭐', 'success')
    
    db.session.commit()
    return redirect(url_for('media.detail', imdb_id=imdb_id))


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """
    User dashboard showing statistics:
    - Total watched, favorites, watchlist count
    - Average rating given
    - Most watched genre
    - Year distribution
    """
    # Basic counts
    total_watched = current_user.watch_history.count()
    total_favorites = current_user.favorites.count()
    total_watchlist = current_user.watchlist.count()
    total_reviews = current_user.reviews.count()
    
    # Average rating
    reviews = current_user.reviews.all()
    avg_rating = 0
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)
    
    # Most watched genre (from watch history)
    history_items = current_user.watch_history.all()
    genre_counter = Counter()
    year_counter = Counter()
    
    for item in history_items:
        # Count genres (each movie can have multiple genres)
        if item.genre:
            for g in item.genre.split(','):
                genre_counter[g.strip()] += 1
        # Count years
        if item.year:
            year_counter[item.year[:4]] += 1
    
    top_genres = genre_counter.most_common(5)
    year_distribution = sorted(year_counter.items())
    
    # Recent activity
    recent_watched = current_user.watch_history.order_by(
        WatchHistory.watched_at.desc()
    ).limit(5).all()
    
    recent_reviews = current_user.reviews.order_by(
        Review.created_at.desc()
    ).limit(5).all()
    
    return render_template(
        'user/dashboard.html',
        total_watched=total_watched,
        total_favorites=total_favorites,
        total_watchlist=total_watchlist,
        total_reviews=total_reviews,
        avg_rating=avg_rating,
        top_genres=top_genres,
        year_distribution=year_distribution,
        recent_watched=recent_watched,
        recent_reviews=recent_reviews,
    )


# ─────────────────────────────────────────────
# COLLECTIONS
# ─────────────────────────────────────────────

@user_bp.route('/collections')
@login_required
def collections():
    """View all user collections."""
    user_collections = current_user.collections.order_by(
        Collection.created_at.desc()
    ).all()
    return render_template('user/collections.html', collections=user_collections)


@user_bp.route('/collections/create', methods=['POST'])
@login_required
def create_collection():
    """Create a new collection."""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    is_public = request.form.get('is_public') == 'on'
    
    if not name:
        flash('Collection name is required.', 'danger')
        return redirect(url_for('user.collections'))
    
    collection = Collection(
        user_id=current_user.id,
        name=name,
        description=description,
        is_public=is_public,
    )
    db.session.add(collection)
    db.session.commit()
    flash(f'Collection "{name}" created! 📚', 'success')
    return redirect(url_for('user.collections'))


@user_bp.route('/collections/<int:collection_id>')
@login_required
def view_collection(collection_id):
    """View items in a collection."""
    collection = Collection.query.filter_by(
        id=collection_id, user_id=current_user.id
    ).first_or_404()
    
    items = collection.items.order_by(CollectionItem.added_at.desc()).all()
    return render_template('user/collection_detail.html',
                           collection=collection, items=items)


@user_bp.route('/collections/add-item', methods=['POST'])
@login_required
def add_to_collection():
    """Add a movie to a collection."""
    collection_id = request.form.get('collection_id', type=int)
    imdb_id = request.form.get('imdb_id')
    title = request.form.get('title')
    
    collection = Collection.query.filter_by(
        id=collection_id, user_id=current_user.id
    ).first_or_404()
    
    existing = CollectionItem.query.filter_by(
        collection_id=collection_id, imdb_id=imdb_id
    ).first()
    
    if not existing:
        item = CollectionItem(
            collection_id=collection_id,
            imdb_id=imdb_id,
            title=title,
            poster=request.form.get('poster'),
            media_type=request.form.get('media_type'),
        )
        db.session.add(item)
        db.session.commit()
        flash(f'Added to "{collection.name}"!', 'success')
    else:
        flash('Already in this collection.', 'info')
    
    return redirect(request.referrer or url_for('user.collections'))


@user_bp.route('/collections/<int:collection_id>/delete', methods=['POST'])
@login_required
def delete_collection(collection_id):
    """Delete a collection."""
    collection = Collection.query.filter_by(
        id=collection_id, user_id=current_user.id
    ).first_or_404()
    
    name = collection.name
    db.session.delete(collection)
    db.session.commit()
    flash(f'Collection "{name}" deleted.', 'success')
    return redirect(url_for('user.collections'))
