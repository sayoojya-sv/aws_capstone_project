# aws_app.py
from flask import Flask, render_template, redirect, url_for, session, flash
import os
import boto3
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

# Import auth blueprint
from auth import auth

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'your_secret_key_here'

# Register blueprint
app.register_blueprint(auth, url_prefix='/auth')

# AWS Configuration
REGION = 'us-east-1' 
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:522814706478:aws_capstone_project'

# Boto3 Resources
dynamodb = boto3.resource('dynamodb', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

# DynamoDB Tables
users_table = dynamodb.Table('Users')
doctors_table = dynamodb.Table('Doctors')
appointments_table = dynamodb.Table('Appointments')
records_table = dynamodb.Table('PatientRecords')

# Helper Functions
def send_notification(subject, message):
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
    except ClientError as e:
        print(f"Error sending notification: {e}")

def get_current_user():
    if 'username' in session:
        response = users_table.get_item(Key={'username': session['username']})
        return response.get('Item')
    return None

@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())

# --- Routes ---
@app.route('/')
def index():
    if 'username' in session:
        user = get_current_user()
        if user:
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('patient_dashboard'))
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Patient, Doctor, Admin routes, Wrapper classes remain the same as in your original code
# Only authentication routes moved to blueprint

if __name__ == '__main__':
    try:
        users_table.load()
    except:
        print("Note: Create DynamoDB tables manually or via script.")
    app.run(host='0.0.0.0', port=5000, debug=True)
