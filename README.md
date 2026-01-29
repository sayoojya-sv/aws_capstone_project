-NexGen Hospital Appointment Booking System

A modern, full-featured hospital appointment booking system built with Flask, featuring patient appointment management, admin approval workflows, and comprehensive patient records management.

-Features

-For Patients
--User Registration & Login - Secure authentication system
--Book Appointments - Easy appointment booking with doctor selection
--Real-time Slot Availability- Check available slots before booking
--Appointment Tracking - View all appointments with status (pending/approved/rejected)
--Medical Records - Access complete medical history

-For Admins
--Admin Dashboard- Comprehensive overview of hospital operations
--Appointment Approval - Review and approve/reject appointment requests
--Slot Management - Configure daily appointment limits for each doctor
--Patient Management - View all patients and their records
--Medical Records - Add and manage patient medical records

-Technology Stack

--Backend: Python 3.11.6, Flask
--Database: SQLite (easily upgradeable to PostgreSQL/MySQL)
--Authentication: Flask-Login
--Frontend: HTML5, CSS3 
--JavaScript: Vanilla JS for interactions

-Prerequisites

--Python 3.7 or higher
--pip (Python package manager)

-Installation & Setup

1. Clone or Navigate to the Project Directory

cd c:\Users\sayoojya\OneDrive\Desktop\aws-project\nexgen-patient-app

2. Create a Virtual Environment

python -m venv venv

3. Activate the Virtual Environment

-Windows:

venv\Scripts\activate

-macOS/Linux:
--source venv/bin/activate

4. Install Dependencies

pip install -r requirements.txt

5. Initialize the Database

python init_db.py

This will:
- Create all necessary database tables
- Create a default admin account (username: `admin`, password: `admin123`)
- Seed sample doctors

6. Run the Application

python app.py

The application will be available at: **http://localhost:5000**

--Default Login Credentials

-Admin Account
--Username: "admin"
--Password: "admin123"

-Patient Account
--Register a new account at `/register`

--Project Structure

nexgen-patient-app/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── config.py              # Configuration settings
├── init_db.py             # Database initialization script
├── requirements.txt       # Python dependencies
├── routes/
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   ├── patient.py        # Patient routes
│   └── admin.py          # Admin routes
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── patient/
│   │   ├── dashboard.html
│   │   ├── book_appointment.html
│   │   ├── appointments.html
│   │   └── records.html
│   └── admin/
│       ├── dashboard.html
│       ├── appointments.html
│       ├── set_slots.html
│       ├── patients.html
│       ├── patient_records.html
│       └── add_record.html
└── static/
    ├── css/
    │   └── style.css     # Modern CSS with glassmorphism
    └── js/
        └── main.js       # JavaScript utilities
```

Design Features

- Modern Glassmorphism UI- Stunning visual effects
- Gradient Backgrounds - Vibrant color schemes
- Smooth Animations - Enhanced user experience
- Responsive Design - Works on all devices
- Interactive Elements - Hover effects and transitions
- Real-time Updates - Dynamic slot availability checking

Security Features

- Password hashing with Werkzeug
- Session management with Flask-Login
- CSRF protection with Flask-WTF
- Role-based access control (Patient/Admin)

--Database Schema

-Users Table
- id, username, email, password_hash, role, created_at

-Doctors Table
- id, name, specialization, available_slots_per_day, created_at

-Appointments Table
- id, patient_id, doctor_id, appointment_date, appointment_time, status, reason, created_at

-Patient Records Table
- id, patient_id, doctor_id, diagnosis, prescription, visit_date, notes, created_at

-Usage Guide

--For Patients

1. Register: Create a new account at `/register`
2. Login: Sign in with your credentials
3. Book Appointment: 
   - Select a doctor and specialization
   - Choose date and time
   - Check real-time slot availability
   - Submit for approval
4. Track Appointments: View status (pending/approved/rejected)
5. View Records: Access your medical history

--For Admins

1. Login: Use admin credentials
2. Dashboard: View statistics and pending appointments
3. Approve Appointments: Review and approve/reject requests
4. Manage Slots: Set daily appointment limits for doctors
5. Patient Management: View all patients and their records
6. Add Records: Create medical records for patients

--Configuration

Edit `config.py` to customize:
- Secret key
- Database URI
- Session settings

--API Endpoints

Authentication
- `GET/POST /register` - User registration
- `GET/POST /login` - User/Admin login
- `GET /logout` - Logout

--Patient Routes
- `GET /patient/dashboard` - Patient dashboard
- `GET/POST /patient/book-appointment` - Book appointment
- `GET /patient/appointments` - View appointments
- `GET /patient/records` - View medical records
- `GET /patient/check-slots/<doctor_id>/<date>` - Check availability

--Admin Routes
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/appointments` - View all appointments
- `GET /admin/approve/<id>` - Approve appointment
- `GET /admin/reject/<id>` - Reject appointment
- `GET/POST /admin/set-slots` - Manage doctor slots
- `GET /admin/patients` - View all patients
- `GET /admin/patient/<id>/records` - View patient records
- `GET/POST /admin/add-record/<patient_id>` - Add medical record

--Troubleshooting

Database Issues:

Delete the database and reinitialize
rm hospital.db
python init_db.py


Port Already in Use:
Edit `app.py` and change the port number in the last line.


Developer

Built with using Flask and modern web technologies.

Acknowledgments

- Flask framework and extensions
- Google Fonts (Inter)
- Modern CSS design patterns

For production deployment, please:

1. Change the SECRET_KEY in config.py
2. Use a production database (PostgreSQL/MySQL)
3. Enable HTTPS
4. Set DEBUG=False
5. Implement additional security measures
