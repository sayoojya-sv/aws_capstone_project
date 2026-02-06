from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

# Initialize AWS DynamoDB (use same region and tables)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table('Users')

# SNS if you want notifications
sns = boto3.client('sns', region_name='us-east-1')
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:522814706478:aws_capstone_project'

def send_notification(subject, message):
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
    except ClientError as e:
        print(f"Error sending notification: {e}")


# Create blueprint
auth = Blueprint('auth', __name__)

# --- Routes ---

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
            send_notification("User Login", f"User {username} has logged in.")

            if item['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif item['role'] == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('patient_dashboard'))
        flash("Invalid credentials!", "danger")
    return render_template('auth/login.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        dob = request.form.get('dob')

        # Check if user exists
        response = users_table.get_item(Key={'username': username})
        if 'Item' in response:
            flash("User already exists!", "warning")
            return redirect(url_for('auth.signup'))

        hashed_password = generate_password_hash(password)

        users_table.put_item(Item={
            'username': username,
            'email': email,
            'password_hash': hashed_password,
            'role': 'patient',
            'date_of_birth': dob,
            'created_at': datetime.utcnow().isoformat()
        })

        send_notification("New User Signup", f"User {username} has signed up.")
        flash("Signup successful! Please login.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))
