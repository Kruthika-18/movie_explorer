# 🎬 MovieHub Explorer – Movie & TV Show Explorer

A full-stack web application built with **Flask (Python)**, **SQLite**, and **OMDb API**.  
Built as an internship project following industry best practices.

---

## 📁 Project Structure

```
movie_explorer/
├── run.py                    ← Entry point (run this!)
├── config.py                 ← App configuration (dev/prod)
├── requirements.txt          ← Python dependencies
├── Procfile                  ← For deployment on Render/Railway
├── .env                      ← Your secret keys (DON'T commit!)
├── .env.example              ← Template for .env
├── .gitignore
├── README.md
└── app/
    ├── __init__.py           ← App factory (creates Flask app)
    ├── models.py             ← Database models (ORM)
    ├── routes/
    │   ├── main.py           ← Home, search, filter routes
    │   ├── auth.py           ← Login, register, logout
    │   ├── media.py          ← Movie detail pages
    │   └── user.py           ← Watchlist, favorites, dashboard
    ├── services/
    │   └── omdb.py           ← OMDb API integration
    ├── templates/
    │   ├── base.html         ← Master layout (navbar, footer)
    │   ├── index.html        ← Home page
    │   ├── search.html       ← Search results
    │   ├── filter.html       ← Browse & filter page
    │   ├── macros/
    │   │   └── media_card.html ← Reusable movie card component
    │   ├── auth/
    │   │   ├── login.html
    │   │   └── register.html
    │   ├── media/
    │   │   └── detail.html   ← Full movie detail page
    │   └── user/
    │       ├── watchlist.html
    │       ├── favorites.html
    │       ├── history.html
    │       ├── dashboard.html
    │       ├── collections.html
    │       └── collection_detail.html
    └── static/
        ├── css/style.css     ← Custom styles
        ├── js/main.js        ← Frontend JavaScript
        └── images/
            └── no-poster.jpg ← Fallback image
```

---



### Step 1: Clone / Download the project
```bash
# If using git:
git clone <your-repo-url>
cd movie_explorer

# Or just extract the ZIP file
```

### Step 2: Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

> ✅ You should see `(venv)` in your terminal prompt

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
```bash
# Copy the example file
copy .env.example .env        # Windows
cp .env.example .env          # Mac/Linux

# Edit .env with your API key
# OMDB_API_KEY=your_key_here
```

### Step 5: Run the Application
```bash
python run.py
```

🌐 Open your browser at: **http://127.0.0.1:5000**

---

## 🗃️ Database Schema (SQL)

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Watchlist
CREATE TABLE watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    imdb_id VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    year VARCHAR(10),
    poster VARCHAR(500),
    media_type VARCHAR(20),
    genre VARCHAR(200),
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, imdb_id)
);

-- Favorites
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    imdb_id VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    year VARCHAR(10),
    poster VARCHAR(500),
    media_type VARCHAR(20),
    genre VARCHAR(200),
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, imdb_id)
);

-- Watch History
CREATE TABLE watch_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    imdb_id VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    year VARCHAR(10),
    poster VARCHAR(500),
    media_type VARCHAR(20),
    genre VARCHAR(200),
    watched_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Reviews / Ratings
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    imdb_id VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, imdb_id)
);

-- Custom Collections
CREATE TABLE collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Collection Items
CREATE TABLE collection_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL REFERENCES collections(id),
    imdb_id VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    poster VARCHAR(500),
    media_type VARCHAR(20),
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🌐 API Documentation

### OMDb API

Base URL: `http://www.omdbapi.com/`

| Parameter | Description | Example |
|-----------|-------------|---------|
| `apikey` | Your API key | `183bfd30` |
| `s` | Search by title | `s=batman` |
| `i` | Fetch by IMDb ID | `i=tt0111161` |
| `t` | Fetch exact title | `t=Inception` |
| `type` | Filter type | `movie` or `series` |
| `y` | Filter by year | `y=2020` |
| `page` | Pagination | `page=2` |

**Example Request:**
```
GET http://www.omdbapi.com/?s=batman&type=movie&apikey=183bfd30
```

**Example Response:**
```json
{
  "Search": [
    {
      "Title": "Batman Begins",
      "Year": "2005",
      "imdbID": "tt0372784",
      "Type": "movie",
      "Poster": "https://..."
    }
  ],
  "totalResults": "42",
  "Response": "True"
}
```

---

## 🐛 Common Errors & Debugging

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: flask` | Virtual env not activated | Run `venv\Scripts\activate` |
| `Response: False` from API | Invalid API key or bad query | Check your `.env` OMDB_API_KEY |
| `OperationalError: no such table` | DB not initialized | Run `python run.py` (auto-creates tables) |
| `jinja2.exceptions.TemplateNotFound` | Wrong template path | Check templates folder structure |
| `OSError: [Errno 98] Address already in use` | Port 5000 busy | Change port in `run.py` or kill old process |

---





### What I Built:
- Full-stack Python web application using Flask framework
- Integrated real movie database API (OMDb) with 1M+ titles
- User authentication with secure password hashing (Werkzeug)
- Complete CRUD operations for watchlists, favorites, collections
- Interactive dashboard with Chart.js statistics
- Deployed to cloud hosting (Render/Railway)

### Design Patterns Used:
- **MVC Pattern**: Models (SQLAlchemy), Views (Jinja2 templates), Controllers (Flask routes)
- **Blueprint Pattern**: Organized routes into logical groups (auth, media, user)
- **Application Factory**: `create_app()` for flexible testing/deployment
- **Service Layer**: `OMDbService` class separates API logic from routes

### Database Design:
- Normalized SQLite schema with 7 tables
- Foreign key relationships between User and all feature tables
- Unique constraints prevent duplicate entries
- Designed to work with PostgreSQL in production (just change DATABASE_URL)

### Security Features:
- Passwords never stored in plain text (bcrypt hashing via Werkzeug)
- CSRF protection via Flask-WTF
- Environment variables for API keys (never hardcoded)
- Login required decorators protect user routes
- SQL injection protection via SQLAlchemy ORM

### Challenges Solved:
1. OMDb free tier has no genre filter → Solved with search-based simulation
2. No recommendations endpoint → Solved with genre-based search queries
3. Session management → Solved with Flask-Login extension
4. Image loading errors → Solved with `onerror` fallback in HTML

---

## 📖 User Guide

### For New Users:
1. Visit the home page and search for any movie
2. Click on a movie card to see full details
3. Register for a free account to unlock all features
4. Add movies to your Watchlist to remember to watch
5. Mark movies as Watched to build your history
6. Rate and review movies you've seen
7. Check your Dashboard for watching statistics
8. Create custom Collections to organize your movies


