from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Doctor, Appointment, PatientRecord
from datetime import datetime
from functools import wraps

# Define the Blueprint for Admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """
    Decorator to ensure the current user has 'admin' role.
    Redirects to index with an error message if access is denied.
    """
    @wraps(f)
    @login_required # Ensure user is logged in first
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access denied. Admins only.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    Render User Admin Dashboard.
    Collects and displays key statistics:
    - Total patients
    - Total appointments
    - Pending/Approved appointment counts
    - Active doctors count
    - List of recent pending appointments
    """
    # Get statistics
    total_patients = User.query.filter_by(role='patient').count()
    total_appointments = Appointment.query.count()
    pending_appointments = Appointment.query.filter_by(status='pending').count()
    approved_appointments = Appointment.query.filter_by(status='approved').count()
    total_doctors = Doctor.query.count()
    
    # Get recent pending appointments
    recent_pending = Appointment.query.filter_by(status='pending')\
        .order_by(Appointment.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_patients=total_patients,
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments,
                         approved_appointments=approved_appointments,
                         total_doctors=total_doctors,
                         recent_pending=recent_pending)


@admin_bp.route('/appointments')
@admin_required
def appointments():
    """
    View all appointments with optional filtering by status (pending, approved, rejected).
    """
    status_filter = request.args.get('status', 'all')
    
    doctors = Doctor.query.all()
    
    if status_filter == 'all':
        all_appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    else:
        all_appointments = Appointment.query.filter_by(status=status_filter)\
            .order_by(Appointment.created_at.desc()).all()
    
    return render_template('admin/appointments.html', 
                         appointments=all_appointments,
                         doctors=doctors,
                         status_filter=status_filter)


@admin_bp.route('/approve/<int:appointment_id>')
@admin_required
def approve_appointment(appointment_id):
    """
    Approve a specific appointment.
    Updates the status to 'approved'.
    """
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.status == 'approved':
        flash('Appointment is already approved!', 'info')
        return redirect(url_for('admin.appointments'))
    
    appointment.status = 'approved'
    
    try:
        db.session.commit()
        flash(f'Appointment #{appointment_id} approved successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while approving the appointment.', 'error')
    
    return redirect(url_for('admin.appointments'))


@admin_bp.route('/reject/<int:appointment_id>')
@admin_required
def reject_appointment(appointment_id):
    """
    Reject a specific appointment.
    Updates the status to 'rejected'.
    """
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.status == 'rejected':
        flash('Appointment is already rejected!', 'info')
        return redirect(url_for('admin.appointments'))
    
    appointment.status = 'rejected'
    
    try:
        db.session.commit()
        flash(f'Appointment #{appointment_id} rejected.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while rejecting the appointment.', 'error')
    
    return redirect(url_for('admin.appointments'))


@admin_bp.route('/set-slots', methods=['GET', 'POST'])
@admin_required
def set_slots():
    """
    Manage doctor availability.
    Sets the number of appointment slots available per day for a selected doctor.
    """
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        slots = request.form.get('slots')
        
        if not doctor_id or not slots:
            flash('Please select a doctor and enter slot limit!', 'error')
            return redirect(url_for('admin.set_slots'))
        
        try:
            slots = int(slots)
            if slots < 1:
                flash('Slot limit must be at least 1!', 'error')
                return redirect(url_for('admin.set_slots'))
            
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                flash('Doctor not found!', 'error')
                return redirect(url_for('admin.set_slots'))
            
            doctor.available_slots_per_day = slots
            db.session.commit()
            
            flash(f'Slot limit for Dr. {doctor.name} updated to {slots} slots per day!', 'success')
            return redirect(url_for('admin.set_slots'))
            
        except ValueError:
            flash('Invalid slot number!', 'error')
            return redirect(url_for('admin.set_slots'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('admin.set_slots'))
    
    # GET request
    doctors = Doctor.query.all()
    return render_template('admin/set_slots.html', doctors=doctors)


@admin_bp.route('/patients')
@admin_required
def patients():
    """
    View complete list of registered patients.
    """
    all_patients = User.query.filter_by(role='patient').all()
    return render_template('admin/patients.html', patients=all_patients)


@admin_bp.route('/patient/<int:patient_id>/records')
@admin_required
def patient_records(patient_id):
    """
    View medical records for a specific patient.
    Accessible by admins for oversight.
    """
    patient = User.query.get_or_404(patient_id)
    
    if patient.role != 'patient':
        flash('Invalid patient ID!', 'error')
        return redirect(url_for('admin.patients'))
    
    records = PatientRecord.query.filter_by(patient_id=patient_id)\
        .order_by(PatientRecord.visit_date.desc()).all()
    
    return render_template('admin/patient_records.html', patient=patient, records=records)


@admin_bp.route('/doctors')
@admin_required
def manage_doctors():
    """
    View list of all doctors in the system.
    """
    all_doctors = Doctor.query.all()
    return render_template('admin/manage_doctors.html', doctors=all_doctors)


@admin_bp.route('/create-doctor', methods=['GET', 'POST'])
@admin_required
def create_doctor():
    """
    Register a new doctor.
    Creates both a User account (for login) and a Doctor profile.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        specialization = request.form.get('specialization')
        slots = request.form.get('slots', '10')
        
        if not all([username, email, password, name, specialization]):
            flash('Please fill all required fields!', 'error')
            return redirect(url_for('admin.create_doctor'))
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('admin.create_doctor'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return redirect(url_for('admin.create_doctor'))
        
        try:
            slots_int = int(slots)
            if slots_int < 1:
                flash('Slots must be at least 1!', 'error')
                return redirect(url_for('admin.create_doctor'))
            
            # Create user account
            new_user = User(
                username=username,
                email=email,
                role='doctor'
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush()  # Get the user ID
            
            # Create doctor profile
            new_doctor = Doctor(
                user_id=new_user.id,
                name=name,
                specialization=specialization,
                available_slots_per_day=slots_int
            )
            db.session.add(new_doctor)
            db.session.commit()
            
            flash(f'Doctor account created successfully! Username: {username}', 'success')
            return redirect(url_for('admin.manage_doctors'))
            
        except ValueError:
            flash('Invalid slot number!', 'error')
            return redirect(url_for('admin.create_doctor'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('admin.create_doctor'))
    
    # GET request
    return render_template('admin/create_doctor.html')


@admin_bp.route('/patient/<int:patient_id>/add-record', methods=['GET', 'POST'])
@admin_required
def add_record(patient_id):
    """
    Add a new medical record for a patient.
    Allows admins to manually enter record data on behalf of a doctor if needed.
    """
    patient = User.query.get_or_404(patient_id)
    
    if patient.role != 'patient':
        flash('Invalid patient ID!', 'error')
        return redirect(url_for('admin.patients'))
    
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        visit_date_str = request.form.get('visit_date')
        notes = request.form.get('notes')
        
        if not all([doctor_id, diagnosis, visit_date_str]):
            flash('Please fill required fields (Doctor, Diagnosis, Date)!', 'error')
            return redirect(url_for('admin.add_record', patient_id=patient_id))
        
        try:
            visit_date = datetime.strptime(visit_date_str, '%Y-%m-%d').date()
            
            record = PatientRecord(
                patient_id=patient.id,
                doctor_id=doctor_id,
                diagnosis=diagnosis,
                prescription=prescription,
                visit_date=visit_date,
                notes=notes
            )
            
            db.session.add(record)
            db.session.commit()
            
            flash('Medical record added successfully!', 'success')
            return redirect(url_for('admin.patient_records', patient_id=patient.id))
            
        except ValueError:
            flash('Invalid date format!', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding record: {str(e)}', 'error')
            
    # GET request
    doctors = Doctor.query.all()
    return render_template('admin/add_record.html', patient=patient, doctors=doctors)
