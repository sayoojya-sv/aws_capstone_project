from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    User model for storing authentication details and general user information.
    This model serves as the base for Patients, Admins, and potentially linked Doctors.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) # Used for login and communications
    password_hash = db.Column(db.String(255), nullable=False) # Stored securely hashed
    role = db.Column(db.String(20), nullable=False, default='patient')  # Role-based access control: 'patient', 'admin', or 'doctor'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_birth = db.Column(db.Date, nullable=True) # Required for patients
    
    # Relationships to other models
    # A patient can have multiple appointments
    appointments = db.relationship('Appointment', backref='patient', lazy=True, foreign_keys='Appointment.patient_id')
    # A patient has medical records created by doctors
    patient_records = db.relationship('PatientRecord', backref='patient', lazy=True)
    # If the user is a doctor, this links to their professional profile
    doctor_profile = db.relationship('Doctor', backref='user', lazy=True, uselist=False)
    
    @property
    def age(self):
        """
        Calculate and return the user's age based on their date of birth.
        Returns None if date_of_birth is not set.
        """
        if not self.date_of_birth:
            return None
        today = datetime.now().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    def set_password(self, password):
        """
        Hashes the provided password and stores it in the password_hash field.
        Always use this method to set passwords.
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verifies if the provided password matches the stored hash.
        Returns True if accurate, False otherwise.
        """
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Doctor(db.Model):
    """
    Doctor model representing medical professionals.
    Linked to a User account for authentication.
    """
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=True)  # Link to User for login credentials
    name = db.Column(db.String(100), nullable=False) # Professional name displayed to patients
    specialization = db.Column(db.String(100), nullable=False) # e.g., "Cardiology", "General Physician"
    available_slots_per_day = db.Column(db.Integer, default=10) # Daily appointment capacity
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    patient_records = db.relationship('PatientRecord', backref='doctor', lazy=True)
    
    def __repr__(self):
        return f'<Doctor {self.name} - {self.specialization}>'


class Appointment(db.Model):
    """
    Appointment model representing a scheduled meeting between a Patient and a Doctor.
    """
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(10), nullable=False)  # Format: "09:00 AM"
    status = db.Column(db.String(20), default='pending')  # Status workflow: 'pending' -> 'approved' or 'rejected'
    reason = db.Column(db.Text) # Reason for visit provided by patient
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.status}>'


class PatientRecord(db.Model):
    """
    Patient medical records created by Doctors.
    Stores diagnosis, prescriptions, and notes from a specific visit.
    """
    __tablename__ = 'patient_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text)
    visit_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text) # Internal notes for the doctor or details for the patient
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PatientRecord {self.id} - Patient {self.patient_id}>'
