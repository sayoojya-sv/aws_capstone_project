# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import boto3

auth = Blueprint('auth', __name__, template_folder='templates')

# DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table('Users')

# Signup Route
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        response = users_table.get_item(Key={'username': username})
        if 'Item' in response:
            flash("User already exists!", "danger")
            return redirect(url_for('auth.signup'))

        hashed_password = generate_password_hash(password)
        users_table.put_item(Item={
            'username': username,
            'email': email,
            'password_hash': hashed_password,
            'role': 'patient',
            'created_at': datetime.utcnow().isoformat()
        })
        flash("Signup successful! Please login.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# Login Route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        response = users_table.get_item(Key={'username': username})
        item = response.get('Item')

        if item and check_password_hash(item['password_hash'], password):
            session['username'] = item['username']
            session['role'] = item['role']
            flash("Login successful!", "success")
            # Redirect based on role
            if item['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif item['role'] == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('patient_dashboard'))
        flash("Invalid credentials!", "danger")
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


# Logout Route
@auth.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))
