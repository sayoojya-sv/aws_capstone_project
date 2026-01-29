from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Doctor, Appointment, PatientRecord
from datetime import datetime
from functools import wraps

# Define Blueprint for Doctor routes
doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

def doctor_required(f):
    """
    Decorator to ensure the current user has 'doctor' role.
    Redirects to index if access is denied.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'doctor':
            flash('Access denied. Doctors only.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@doctor_bp.route('/dashboard')
@doctor_required
def dashboard():
    """
    Render Doctor Dashboard.
    Displays:
    - Recent appointments (limit 5)
    - Total, Pending, and Approved appointment counts
    - Total patient records created count
    """
    # Get doctor profile associated with current user
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        flash('Doctor profile not found!', 'error')
        return redirect(url_for('index'))
    
    # Get recent appointments
    recent_appointments = Appointment.query.filter_by(doctor_id=doctor.id)\
        .order_by(Appointment.appointment_date.desc()).limit(5).all()
    
    # Get statistics
    total_appointments = Appointment.query.filter_by(doctor_id=doctor.id).count()
    pending_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status='pending').count()
    approved_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status='approved').count()
    total_records = PatientRecord.query.filter_by(doctor_id=doctor.id).count()
    
    return render_template('doctor/dashboard.html',
                         doctor=doctor,
                         recent_appointments=recent_appointments,
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments,
                         approved_appointments=approved_appointments,
                         total_records=total_records)


@doctor_bp.route('/appointments')
@doctor_required
def appointments():
    """
    View all appointments for the current doctor.
    Supports filtering by status.
    """
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        flash('Doctor profile not found!', 'error')
        return redirect(url_for('index'))
    
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        all_appointments = Appointment.query.filter_by(doctor_id=doctor.id)\
            .order_by(Appointment.appointment_date.desc()).all()
    else:
        all_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status=status_filter)\
            .order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('doctor/appointments.html', 
                         appointments=all_appointments,
                         status_filter=status_filter,
                         doctor=doctor)


@doctor_bp.route('/records')
@doctor_required
def records():
    """
    View all patient records created by this doctor, grouped by patient.
    """
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        flash('Doctor profile not found!', 'error')
        return redirect(url_for('index'))
    
    # Group records by patient
    patients_map = {}
    all_records = PatientRecord.query.filter_by(doctor_id=doctor.id)\
        .order_by(PatientRecord.visit_date.desc()).all()
    
    for record in all_records:
        if record.patient not in patients_map:
            patients_map[record.patient] = []
        patients_map[record.patient].append(record)
    
    # Sort patients alphabetically by username
    sorted_patients_map = dict(sorted(patients_map.items(), key=lambda item: item[0].username.lower()))
    
    return render_template('doctor/records.html', patients_map=sorted_patients_map, doctor=doctor)


@doctor_bp.route('/patient-records/<int:patient_id>')
@doctor_required
def patient_records_view(patient_id):
    """
    View full medical history for a specific patient.
    Includes records from all doctors, allowing for comprehensive care.
    """
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found!', 'error')
        return redirect(url_for('index'))
        
    patient = User.query.get_or_404(patient_id)
    
    # Show all records for this patient (history from all doctors)
    records = PatientRecord.query.filter_by(patient_id=patient_id)\
        .order_by(PatientRecord.visit_date.desc()).all()
        
    return render_template('doctor/patient_full_records.html', patient=patient, records=records)


@doctor_bp.route('/add-record/<int:patient_id>', methods=['GET', 'POST'])
@doctor_required
def add_record(patient_id):
    """
    Add a new medical record for a patient.
    Collects diagnosis, prescription, date, and notes.
    """
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        flash('Doctor profile not found!', 'error')
        return redirect(url_for('doctor.dashboard'))
    
    patient = User.query.get_or_404(patient_id)
    
    if patient.role != 'patient':
        flash('Invalid patient ID!', 'error')
        return redirect(url_for('doctor.appointments'))
    
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        visit_date = request.form.get('visit_date')
        notes = request.form.get('notes')
        
        if not all([diagnosis, visit_date]):
            flash('Please fill all required fields!', 'error')
            return redirect(url_for('doctor.add_record', patient_id=patient_id))
        
        try:
            visit_date_obj = datetime.strptime(visit_date, '%Y-%m-%d').date()
            
            new_record = PatientRecord(
                patient_id=patient_id,
                doctor_id=doctor.id,
                diagnosis=diagnosis,
                prescription=prescription,
                visit_date=visit_date_obj,
                notes=notes
            )
            
            db.session.add(new_record)
            db.session.commit()
            
            flash('Patient record added successfully!', 'success')
            return redirect(url_for('doctor.records'))
            
        except ValueError:
            flash('Invalid date format!', 'error')
            return redirect(url_for('doctor.add_record', patient_id=patient_id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('doctor.add_record', patient_id=patient_id))
    
    # GET request
    return render_template('doctor/add_record.html', patient=patient, doctor=doctor)
