from flask import Flask, render_template, request
from flask_login import LoginManager
from models import db, User
from config import Config
import os

# Initialize Flask application
app = Flask(__name__)

# Load configuration from Config class
app.config.from_object(Config)

# Initialize database with the app
db.init_app(app)

# Initialize Flask-Login for user authentication management
login_manager = LoginManager()
login_manager.init_app(app)

# Standardize login view and messages
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """
    Callback to reload the user object from the user ID stored in the session.
    Required by Flask-Login.
    """
    return User.query.get(int(user_id))

# Import and register blueprints for modular application structure
# Auth Blueprint: Handles login, registration, password reset
from routes.auth import auth_bp
# Patient Blueprint: Handles patient dashboard, appointments, medical records
from routes.patient import patient_bp
# Admin Blueprint: Handles system administration, doctor management, patient records
from routes.admin import admin_bp
# Doctor Blueprint: Handles doctor dashboard, appointments, patient records
from routes.doctor import doctor_bp

app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(doctor_bp)

# Home route - Landing page of the application
@app.route('/')
def index():
    return render_template('index.html')




# About page route
@app.route('/about')
def about():
    return render_template('about.html')


# Contact page route - Handles both display and form submission
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        from flask import flash
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # In a real application, you would send this to an email or save to database
        # For now, we just flash a success message
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return render_template('contact.html')
    
    return render_template('contact.html')

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
    
    # Run the application in debug mode
    app.run(debug=True, host='0.0.0.0', port=5000)
