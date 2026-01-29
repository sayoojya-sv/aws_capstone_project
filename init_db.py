from app import app, db
from models import User, Doctor
from datetime import date

def init_database():
    """
    Initialize database with tables and sample data.
    This script is intended to be run once to set up the environment.
    """
    with app.app_context():
        try:
            # Create all tables defined in models.py
            db.create_all()
            print("✓ Database tables created")
            
            # Check if default admin already exists to avoid duplication
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                # Create default admin account
                admin = User(
                    username='admin',
                    email='admin@hospital.com',
                    role='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                print("✓ Admin account created (username: admin, password: admin123)")
            else:
                print("✓ Admin account already exists")
            
            # Check if any doctors exist to give feedback
            doctor_count = Doctor.query.count()
            print(f"✓ Doctors check: {doctor_count} doctors found")
            
            # Commit all changes to the database
            db.session.commit()
            print("\n✅ Database initialization completed successfully!")
            print("\n📝 Login Credentials:")
            print("   Admin - username: admin, password: admin123")
            print("\n🏥 Available Doctors:")
            doctors_list = Doctor.query.all()
            for doctor in doctors_list:
                print(f"   • {doctor.name} - {doctor.specialization} ({doctor.available_slots_per_day} slots/day)")
                
        except Exception as e:
            # Rollback changes if any error occurs to ensure database integrity
            db.session.rollback()
            print(f"\n❌ Error during initialization: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    init_database()
