"""
app/routes/main.py - Main Routes
----------------------------------
Handles the home page and search functionality.
Blueprint = a way to organize related routes.
"""

from flask import Blueprint, render_template, request, flash
from app.services.omdb import OMDbService

# Create a Blueprint named 'main'
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Home page route.
    Shows trending/featured content and search bar.
    """
    try:
        omdb = OMDbService()
        
        # Get some featured content for the home page
        featured_titles = ['Inception', 'The Dark Knight', 'Interstellar', 
                          'Avengers', 'Breaking Bad', 'Stranger Things']
        featured = []
        for title in featured_titles:
            data = omdb.get_by_title(title)
            if data:
                featured.append(data)
        
        # Get upcoming releases
        upcoming = omdb.get_upcoming()
        
    except Exception as e:
        featured = []
        upcoming = []
    
    return render_template('index.html', featured=featured, upcoming=upcoming)


@main_bp.route('/search')
def search():
    """
    Search results route.
    Gets query from URL parameter: /search?q=batman&type=movie&year=2020
    """
    # Get search parameters from URL
    query = request.args.get('q', '').strip()
    media_type = request.args.get('type', '')
    year = request.args.get('year', '')
    imdb_rating = request.args.get('rating', '')
    page = request.args.get('page', 1, type=int)
    
    results = []
    total = 0
    total_pages = 0
    
    if query:
        try:
            omdb = OMDbService()
            data = omdb.search(
                query=query,
                media_type=media_type if media_type else None,
                year=year if year else None,
                page=page
            )
            
            if data:
                results = data['results']
                total = data['total']
                # OMDb returns 10 results per page
                total_pages = (total + 9) // 10
            else:
                flash(f'No results found for "{query}". Try different keywords.', 'info')
                
        except Exception as e:
            flash('Error connecting to movie database. Please try again.', 'danger')
    
    return render_template(
        'search.html',
        query=query,
        results=results,
        total=total,
        current_page=page,
        total_pages=total_pages,
        media_type=media_type,
        year=year,
    )


@main_bp.route('/filter')
def filter_media():
    """
    Advanced filtering page with genre, year, rating filters.
    Week 3 feature.
    """
    genre = request.args.get('genre', '')
    year = request.args.get('year', '')
    media_type = request.args.get('type', '')
    page = request.args.get('page', 1, type=int)
    
    results = []
    total = 0
    total_pages = 0
    
    # Build a search query from filters
    search_term = genre if genre else 'popular'
    
    try:
        omdb = OMDbService()
        data = omdb.search(
            query=search_term,
            media_type=media_type if media_type else None,
            year=year if year else None,
            page=page
        )
        if data:
            results = data['results']
            total = data['total']
            total_pages = (total + 9) // 10
    except Exception:
        flash('Error loading filtered results.', 'danger')
    
    # Genre options for the filter dropdown
    genres = ['Action', 'Comedy', 'Drama', 'Horror', 'Romance', 
              'Sci-Fi', 'Thriller', 'Animation', 'Documentary', 'Crime']
    
    return render_template(
        'filter.html',
        results=results,
        total=total,
        current_page=page,
        total_pages=total_pages,
        genres=genres,
        selected_genre=genre,
        selected_year=year,
        selected_type=media_type,
    )
