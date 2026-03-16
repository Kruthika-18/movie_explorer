"""
app/services/omdb.py - OMDb API Integration
---------------------------------------------
This module handles ALL communication with the OMDb API.
Keeping API calls in a separate "service" file is a best practice
(separation of concerns).

OMDb API Docs: https://www.omdbapi.com/
Free tier: 1000 requests/day
"""

import requests
from flask import current_app


class OMDbService:
    """Service class for OMDb API operations."""
    
    def __init__(self):
        """Get API key from app config."""
        self.api_key = current_app.config['OMDB_API_KEY']
        self.base_url = current_app.config['OMDB_BASE_URL']
    
    def _make_request(self, params):
        """
        Private helper method to make API requests.
        Always adds the API key to params.
        Returns parsed JSON or None on error.
        """
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()  # Raises error for 4xx/5xx responses
            data = response.json()
            
            # OMDb returns {"Response": "False"} on errors
            if data.get('Response') == 'False':
                return None
            return data
            
        except requests.exceptions.Timeout:
            current_app.logger.error("OMDb API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"OMDb API error: {e}")
            return None
    
    def search(self, query, media_type=None, year=None, page=1):
        """
        Search for movies/series by title.
        
        Args:
            query: Search term (e.g., "Avengers")
            media_type: 'movie', 'series', or None for all
            year: Release year (optional)
            page: Page number for pagination
        
        Returns:
            dict with 'results' list and 'total' count, or None
        """
        params = {
            's': query,      # 's' = search by title
            'page': page,
            'type': media_type or '',
            'y': year or '',
        }
        
        # Remove empty params
        params = {k: v for k, v in params.items() if v != ''}
        
        data = self._make_request(params)
        if not data:
            return None
        
        return {
            'results': data.get('Search', []),
            'total': int(data.get('totalResults', 0))
        }
    
    def get_details(self, imdb_id):
        """
        Get full details for a movie/series by IMDb ID.
        
        Args:
            imdb_id: IMDb ID string (e.g., "tt0111161")
        
        Returns:
            dict with full movie details, or None
        """
        params = {
            'i': imdb_id,     # 'i' = fetch by IMDb ID
            'plot': 'full',   # Get full plot description
        }
        return self._make_request(params)
    
    def get_by_title(self, title, year=None):
        """
        Get details for a specific title (exact match).
        Used for recommendations.
        """
        params = {
            't': title,
            'y': year or '',
            'plot': 'short',
        }
        params = {k: v for k, v in params.items() if v != ''}
        return self._make_request(params)
    
    def get_recommendations(self, genre, exclude_id=None, count=6):
        """
        Get recommendations based on genre.
        OMDb free tier doesn't have a recommendations endpoint,
        so we search by genre keywords (simulated).
        
        Args:
            genre: Comma-separated genres (e.g., "Action, Drama")
            exclude_id: IMDb ID to exclude from results
            count: Number of recommendations to return
        """
        # Use the first genre for search
        primary_genre = genre.split(',')[0].strip() if genre else 'Drama'
        
        # Search for popular movies in that genre
        genre_keywords = {
            'Action': 'action hero',
            'Comedy': 'comedy funny',
            'Drama': 'drama award',
            'Horror': 'horror scary',
            'Romance': 'romance love',
            'Sci-Fi': 'science fiction space',
            'Thriller': 'thriller suspense',
            'Animation': 'animated adventure',
            'Documentary': 'documentary',
            'Crime': 'crime detective',
        }
        
        search_term = genre_keywords.get(primary_genre, primary_genre)
        data = self.search(search_term, page=1)
        
        if not data:
            return []
        
        results = data.get('results', [])
        
        # Filter out the current movie
        if exclude_id:
            results = [r for r in results if r.get('imdbID') != exclude_id]
        
        return results[:count]
    
    def get_upcoming(self):
        """
        Simulate upcoming releases (OMDb free tier limitation).
        Returns recent popular titles as 'upcoming'.
        """
        upcoming_titles = [
            "Deadpool", "Inside Out", "Dune", 
            "Oppenheimer", "Barbie", "Spider-Man"
        ]
        results = []
        for title in upcoming_titles[:6]:
            data = self.get_by_title(title)
            if data:
                results.append(data)
        return results
