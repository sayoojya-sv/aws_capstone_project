import os
from datetime import timedelta

class Config:
    """
    Base configuration class.
    Contains settings for Flask, Database, Session, and Security.
    """
    # Security Key: Used for session signing and other security related needs.
    # Should be set via environment variable in production.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration: Defaults to SQLite for development.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///hospital.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Disable event system to save memory
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24) # User stays logged in for 24 hours
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS to ensure cookies are only sent over encrypted connections
    SESSION_COOKIE_HTTPONLY = True # Prevent checking cookies via JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax' # CSRF protection for cookies
    
    # Flask-WTF configuration for Forms
    WTF_CSRF_ENABLED = True # Enable Cross-Site Request Forgery protection
    WTF_CSRF_TIME_LIMIT = None # Token validity time
