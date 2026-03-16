"""
app/routes/auth.py - Authentication Routes
--------------------------------------------
Handles user registration, login, and logout.
Flask-Login manages session cookies automatically.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration page.
    GET: Show the registration form.
    POST: Process the form and create the account.
    """
    # If already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # ── Validation ──────────────────────────────
        errors = []
        
        if len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if username/email already taken
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken. Please choose another.')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered. Please log in.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html',
                                   username=username, email=email)
        
        # ── Create User ──────────────────────────────
        user = User(username=username, email=email)
        user.set_password(password)  # Hashes the password!
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Account created successfully! Welcome, {username}!', 'success')
        login_user(user)  # Auto-login after registration
        return redirect(url_for('main.index'))
    
    # GET request - show empty form
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        # Find user in database
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to the page they were trying to access
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log the user out and redirect to home."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/admin/users')
@login_required
def admin_users():
    """
    Admin page - shows all registered users.
    Only accessible if logged in as 'admin'.
    """
    if current_user.username != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('main.index'))
    
    all_users = User.query.order_by(User.created_at.desc()).all()
    
    user_stats = []
    for user in all_users:
        user_stats.append({
            'user': user,
            'watchlist_count': user.watchlist.count(),
            'favorites_count': user.favorites.count(),
            'watched_count': user.watch_history.count(),
            'reviews_count': user.reviews.count(),
        })
    
    return render_template('auth/admin_users.html', user_stats=user_stats, total=len(all_users))
