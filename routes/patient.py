from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Doctor, Appointment, PatientRecord, User
from datetime import datetime, date
from functools import wraps

# Define the Blueprint for Patient routes
patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

def patient_required(f):
    """
    Decorator to ensure the current user has 'patient' role.
    Redirects to index if access is denied.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'patient':
            flash('Access denied. Patients only.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@patient_bp.route('/dashboard')
@patient_required
def dashboard():
    """
    Render Patient Dashboard.
    Displays:
    - Recent appointments (limit 5)
    - Total, Pending, and Approved appointment counts
    """
    # Get recent appointments
    recent_appointments = Appointment.query.filter_by(patient_id=current_user.id)\
        .order_by(Appointment.created_at.desc()).limit(5).all()
    
    # Get statistics
    total_appointments = Appointment.query.filter_by(patient_id=current_user.id).count()
    pending_appointments = Appointment.query.filter_by(patient_id=current_user.id, status='pending').count()
    approved_appointments = Appointment.query.filter_by(patient_id=current_user.id, status='approved').count()
    
    return render_template('patient/dashboard.html',
                         recent_appointments=recent_appointments,
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments,
                         approved_appointments=approved_appointments)


@patient_bp.route('/book-appointment', methods=['GET', 'POST'])
@patient_required
def book_appointment():
    """
    Handle appointment booking.
    - Validates doctor, date, and time selection.
    - Checks for valid dates (no past dates).
    - Checks doctor's daily available slots against approved appointments.
    - Creates a 'pending' appointment request if all checks pass.
    """
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        reason = request.form.get('reason')
        
        # Validation
        if not all([doctor_id, appointment_date, appointment_time]):
            flash('Please fill all required fields!', 'error')
            return redirect(url_for('patient.book_appointment'))
        
        try:
            # Convert date string to date object
            appt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            
            # Check if date is in the past
            if appt_date < date.today():
                flash('Cannot book appointments in the past!', 'error')
                return redirect(url_for('patient.book_appointment'))
            
            # Check if doctor exists
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                flash('Invalid doctor selection!', 'error')
                return redirect(url_for('patient.book_appointment'))
            
            # Check slot availability
            # We count only 'approved' appointments towards the limit
            existing_appointments = Appointment.query.filter_by(
                doctor_id=doctor_id,
                appointment_date=appt_date,
                status='approved'
            ).count()
            
            if existing_appointments >= doctor.available_slots_per_day:
                flash('Sorry, no slots available for this doctor on the selected date!', 'error')
                return redirect(url_for('patient.book_appointment'))
            
            # Create appointment
            new_appointment = Appointment(
                patient_id=current_user.id,
                doctor_id=doctor_id,
                appointment_date=appt_date,
                appointment_time=appointment_time,
                reason=reason,
                status='pending'
            )
            
            db.session.add(new_appointment)
            db.session.commit()
            
            flash('Appointment request submitted successfully! Waiting for admin approval.', 'success')
            return redirect(url_for('patient.appointments'))
            
        except ValueError:
            flash('Invalid date format!', 'error')
            return redirect(url_for('patient.book_appointment'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('patient.book_appointment'))
    
    # GET request - show form
    doctors = Doctor.query.all()
    return render_template('patient/book_appointment.html', doctors=doctors)


@patient_bp.route('/appointments')
@patient_required
def appointments():
    """
    View all appointments for the current patient.
    Supports filtering by status.
    """
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        all_appointments = Appointment.query.filter_by(patient_id=current_user.id)\
            .order_by(Appointment.appointment_date.desc()).all()
    else:
        all_appointments = Appointment.query.filter_by(patient_id=current_user.id, status=status_filter)\
            .order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('patient/appointments.html', 
                         appointments=all_appointments,
                         status_filter=status_filter)


@patient_bp.route('/records')
@patient_required
def records():
    """
    View all medical records for the current patient.
    """
    patient_records = PatientRecord.query.filter_by(patient_id=current_user.id)\
        .order_by(PatientRecord.visit_date.desc()).all()
    
    return render_template('patient/records.html', records=patient_records)


@patient_bp.route('/check-slots/<int:doctor_id>/<appointment_date>')
@patient_required
def check_slots(doctor_id, appointment_date):
    """
    API endpoint to check available slots for a specific doctor on a specific date.
    Returns JSON with available slots count.
    Used by the frontend for real-time validation.
    """
    try:
        appt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        doctor = Doctor.query.get(doctor_id)
        
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        
        # Count approved appointments
        booked_slots = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appt_date,
            status='approved'
        ).count()
        
        available_slots = doctor.available_slots_per_day - booked_slots
        
        return jsonify({
            'available_slots': max(0, available_slots),
            'total_slots': doctor.available_slots_per_day,
            'booked_slots': booked_slots
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@patient_bp.route('/update-profile', methods=['GET', 'POST'])
@patient_required
def update_profile():
    """
    Update patient profile information (Email, DOB).
    """
    if request.method == 'POST':
        email = request.form.get('email')
        dob_str = request.form.get('dob')
        
        if not email or not dob_str:
            flash('All fields are required!', 'error')
            return redirect(url_for('patient.update_profile'))
            
        # Check if email is taken by another user
        existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_user:
            flash('Email already registered by another user!', 'error')
            return redirect(url_for('patient.update_profile'))
            
        try:
            date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            
            # Update user
            current_user.email = email
            current_user.date_of_birth = date_of_birth
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('patient.dashboard'))
            
        except ValueError:
            flash('Invalid date format!', 'error')
            return redirect(url_for('patient.update_profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('patient.update_profile'))
            
    return render_template('patient/update_profile.html')
