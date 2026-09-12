"""
backend/app.py
Flask application factory.
Run with: flask run   OR   python app.py
"""

from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
from sqlalchemy import inspect, text
from .models import db, User, Department, Doctor, Appointment, MonthlyReport
from .auth.routes import auth_bp
from .routes.admin import admin_bp
from .routes.doctor import doctor_bp
from .routes.patient import patient_bp
from werkzeug.security import generate_password_hash
import os


def create_app(config=None):
    app = Flask(__name__)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    is_serverless = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))
    if is_serverless:
        default_db_path = '/tmp/hms.db'
    else:
        root_instance = os.path.abspath(os.path.join(base_dir, '..', 'instance'))
        try:
            os.makedirs(root_instance, exist_ok=True)
            default_db_path = os.path.join(root_instance, 'hms.db')
        except OSError:
            default_db_path = '/tmp/hms.db'

    # ── Config ──
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-in-production-please')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or f'sqlite:///{default_db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Extensions ──
    db.init_app(app)

    # Allow flexible CORS in dev (avoids "load failed" when using LAN/Vite host)
    cors_env = os.environ.get('CORS_ORIGINS', '').strip()
    if cors_env:
        origins = [o.strip() for o in cors_env.split(',') if o.strip()]
    else:
        origins = [
            'http://localhost:5173',
            'http://127.0.0.1:5173',
            'http://localhost:3000',
            'http://127.0.0.1:3000'
        ]
        if app.debug:
            origins = '*'

    supports_credentials = origins != '*'
    CORS(
        app,
        resources={r'/api/*': {'origins': origins}},
        supports_credentials=supports_credentials,
        allow_headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
    )

    # ── Blueprints ──
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')

    # ── DB init + seed ──
    with app.app_context():
        db.create_all()
        ensure_department_uid_schema()
        ensure_doctor_uid_schema()
        ensure_patient_uid_schema()
        ensure_appointment_uid_schema()
        ensure_no_double_booking_index()
        backfill_department_uids()
        backfill_doctor_uids()
        backfill_patient_uids()
        backfill_appointment_uids()
        seed_admin()

    @app.get("/")
    def index():
        return jsonify(
            {
                "message": "HMS backend running",
                "health": "/api/auth/me",
                "login": "/api/auth/patient/login",
            }
        )

    return app


def seed_admin():
    """
    Creates the default admin user programmatically if not already present.
    This is the ONLY way admin is created — no registration route exists.
    Change credentials via environment variables in production.
    """
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@hospital.local')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@1234')

    from .models import User  # Avoid potential circular import
    existing = User.query.filter_by(role='admin').first()
    if not existing:
        admin = User(
            username=admin_username,
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f'[HMS] Admin user created → username: {admin_username}')
    else:
        print('[HMS] Admin already exists, skipping seed.')


def ensure_department_uid_schema():
    inspector = inspect(db.engine)
    if 'departments' not in inspector.get_table_names():
        return
    cols = {c['name'] for c in inspector.get_columns('departments')}
    if 'department_uid' not in cols:
        db.session.execute(text('ALTER TABLE departments ADD COLUMN department_uid VARCHAR(20)'))
        db.session.commit()
    db.session.execute(
        text('CREATE UNIQUE INDEX IF NOT EXISTS ix_departments_department_uid ON departments (department_uid)')
    )
    db.session.commit()


def backfill_department_uids():
    from .models import Department
    departments = Department.query.filter(
        (Department.department_uid.is_(None)) | (Department.department_uid == '')
    ).order_by(Department.id.asc()).all()
    if not departments:
        return

    used = {
        d.department_uid for d in Department.query.filter(Department.department_uid.isnot(None)).all()
        if d.department_uid
    }
    counter = 1
    for dept in departments:
        while True:
            candidate = f'CSDE{counter:03d}'
            counter += 1
            if candidate not in used:
                dept.department_uid = candidate
                used.add(candidate)
                break
    db.session.commit()


def ensure_doctor_uid_schema():
    inspector = inspect(db.engine)
    if 'doctors' not in inspector.get_table_names():
        return
    cols = {c['name'] for c in inspector.get_columns('doctors')}
    missing_doctor_cols = {
        'doctor_uid': 'VARCHAR(20)',
        'gender': 'VARCHAR(20)',
        'sub_specialties': 'TEXT',
        'average_rating': 'FLOAT',
        'languages_spoken': 'TEXT',
        'certifications': 'TEXT',
        'awards': 'TEXT',
        'past_experience': 'TEXT',
        'appointment_fee': 'FLOAT',
    }
    for col, col_type in missing_doctor_cols.items():
        if col not in cols:
            db.session.execute(text(f'ALTER TABLE doctors ADD COLUMN {col} {col_type}'))
            db.session.commit()
    db.session.execute(
        text('CREATE UNIQUE INDEX IF NOT EXISTS ix_doctors_doctor_uid ON doctors (doctor_uid)')
    )
    db.session.commit()


def ensure_patient_uid_schema():
    inspector = inspect(db.engine)
    if 'patients' not in inspector.get_table_names():
        return
    cols = {c['name'] for c in inspector.get_columns('patients')}
    missing_patient_cols = {
        'patient_uid': 'VARCHAR(20)',
        'emergency_contact_name': 'VARCHAR(120)',
        'emergency_contact_relationship': 'VARCHAR(60)',
        'emergency_contact_phone': 'VARCHAR(30)',
        'insurance_provider': 'VARCHAR(120)',
        'insurance_policy_number': 'VARCHAR(80)',
        'insurance_member_id': 'VARCHAR(80)',
        'insurance_coverage_start': 'DATE',
        'allergies': 'TEXT',
        'medications': 'TEXT',
        'conditions': 'TEXT',
        'primary_physician': 'VARCHAR(120)',
        'preferred_language': 'VARCHAR(60)',
        'communication_preferences': 'VARCHAR(120)',
        'accessibility_needs': 'TEXT',
        'occupation': 'VARCHAR(120)',
        'marital_status': 'VARCHAR(40)',
        'blood_type': 'VARCHAR(10)',
        'family_history': 'TEXT',
        'pregnancy_status': 'VARCHAR(40)',
        'preferred_pharmacy': 'VARCHAR(120)',
        'consent_terms': 'BOOLEAN DEFAULT 0',
        'consent_telehealth': 'BOOLEAN DEFAULT 0',
        'consent_reminders': 'BOOLEAN DEFAULT 0',
        'consent_marketing': 'BOOLEAN DEFAULT 0',
        'government_id_type': 'VARCHAR(40)',
        'government_id_number': 'VARCHAR(80)',
    }
    for col, col_type in missing_patient_cols.items():
        if col not in cols:
            db.session.execute(text(f'ALTER TABLE patients ADD COLUMN {col} {col_type}'))
            db.session.commit()
    db.session.execute(
        text('CREATE UNIQUE INDEX IF NOT EXISTS ix_patients_patient_uid ON patients (patient_uid)')
    )
    db.session.commit()


def ensure_appointment_uid_schema():
    inspector = inspect(db.engine)
    if 'appointments' not in inspector.get_table_names():
        return
    cols = {c['name'] for c in inspector.get_columns('appointments')}
    if 'appointment_uid' not in cols:
        db.session.execute(text('ALTER TABLE appointments ADD COLUMN appointment_uid VARCHAR(20)'))
        db.session.commit()
    db.session.execute(
        text('CREATE UNIQUE INDEX IF NOT EXISTS ix_appointments_appointment_uid ON appointments (appointment_uid)')
    )
    db.session.commit()


def ensure_no_double_booking_index():
    inspector = inspect(db.engine)
    if 'appointments' not in inspector.get_table_names():
        return
    # Prevent multiple booked appointments at the same time for the same doctor.
    db.session.execute(
        text(
            'CREATE UNIQUE INDEX IF NOT EXISTS ix_appointments_doctor_dt_booked '
            'ON appointments (doctor_id, appointment_dt) WHERE status = "booked"'
        )
    )
    db.session.commit()


def backfill_appointment_uids():
    from .models import Appointment
    appts = Appointment.query.filter(
        (Appointment.appointment_uid.is_(None)) | (Appointment.appointment_uid == '')
    ).order_by(Appointment.id.asc()).all()
    if not appts:
        return
    for appt in appts:
        year_tag = appt.appointment_dt.strftime('%y') if appt.appointment_dt else None
        appt.appointment_uid = Appointment.format_appointment_uid(appt.id, year_tag)
    db.session.commit()


def backfill_doctor_uids():
    from .models import Doctor
    doctors = Doctor.query.filter(
        (Doctor.doctor_uid.is_(None)) | (Doctor.doctor_uid == '')
    ).order_by(Doctor.id.asc()).all()
    if not doctors:
        return

    used = {
        d.doctor_uid for d in Doctor.query.filter(Doctor.doctor_uid.isnot(None)).all()
        if d.doctor_uid
    }
    counters = {}
    for doc in doctors:
        yy = (doc.created_at or datetime.utcnow()).strftime('%y')
        counters.setdefault(yy, 1)
        while True:
            candidate = f'CS{yy}D{counters[yy]:04d}'
            counters[yy] += 1
            if candidate not in used:
                doc.doctor_uid = candidate
                used.add(candidate)
                break
    db.session.commit()


def backfill_patient_uids():
    from .models import Patient
    patients = Patient.query.filter(
        (Patient.patient_uid.is_(None)) | (Patient.patient_uid == '')
    ).order_by(Patient.id.asc()).all()
    if not patients:
        return

    used = {
        p.patient_uid for p in Patient.query.filter(Patient.patient_uid.isnot(None)).all()
        if p.patient_uid
    }
    # For backfill, use current year unless patient has created_at
    counters = {}
    for p in patients:
        yy = (p.created_at or datetime.utcnow()).strftime('%y')
        counters.setdefault(yy, 1)
        while True:
            candidate = f'CS{yy}P{counters[yy]:04d}'
            counters[yy] += 1
            if candidate not in used:
                p.patient_uid = candidate
                used.add(candidate)
                break
    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
