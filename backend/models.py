"""
backend/models.py
SQLAlchemy models for HMS.
All tables are created programmatically — never use DB Browser.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """
    Base user table — holds auth credentials for all roles.
    role: 'admin' | 'doctor' | 'patient'
    """
    __tablename__ = 'users'

    id             = db.Column(db.Integer, primary_key=True)
    email          = db.Column(db.String(120), unique=True, nullable=True)   # null for admin (uses username)
    username       = db.Column(db.String(80), unique=True, nullable=True)    # only for admin
    password_hash  = db.Column(db.String(256), nullable=False)
    role           = db.Column(db.String(20), nullable=False)                # admin | doctor | patient
    is_active      = db.Column(db.Boolean, default=True)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    patient = db.relationship('Patient', back_populates='user', uselist=False)
    doctor  = db.relationship('Doctor', back_populates='user', uselist=False)

    def __repr__(self):
        return f'<User {self.role}:{self.email or self.username}>'


class Patient(db.Model):
    __tablename__ = 'patients'

    id         = db.Column(db.Integer, primary_key=True)
    patient_uid = db.Column(db.String(20), unique=True, nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name  = db.Column(db.String(80), nullable=False)
    phone      = db.Column(db.String(20), unique=True, nullable=False)
    dob        = db.Column(db.Date, nullable=False)
    gender     = db.Column(db.String(10), nullable=False)
    address    = db.Column(db.Text, nullable=True)
    emergency_contact_name = db.Column(db.String(120), nullable=True)
    emergency_contact_relationship = db.Column(db.String(60), nullable=True)
    emergency_contact_phone = db.Column(db.String(30), nullable=True)
    insurance_provider = db.Column(db.String(120), nullable=True)
    insurance_policy_number = db.Column(db.String(80), nullable=True)
    insurance_member_id = db.Column(db.String(80), nullable=True)
    insurance_coverage_start = db.Column(db.Date, nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    medications = db.Column(db.Text, nullable=True)
    conditions = db.Column(db.Text, nullable=True)
    primary_physician = db.Column(db.String(120), nullable=True)
    preferred_language = db.Column(db.String(60), nullable=True)
    communication_preferences = db.Column(db.String(120), nullable=True)
    accessibility_needs = db.Column(db.Text, nullable=True)
    occupation = db.Column(db.String(120), nullable=True)
    marital_status = db.Column(db.String(40), nullable=True)
    blood_type = db.Column(db.String(10), nullable=True)
    family_history = db.Column(db.Text, nullable=True)
    pregnancy_status = db.Column(db.String(40), nullable=True)
    preferred_pharmacy = db.Column(db.String(120), nullable=True)
    consent_terms = db.Column(db.Boolean, default=False, nullable=False)
    consent_telehealth = db.Column(db.Boolean, default=False)
    consent_reminders = db.Column(db.Boolean, default=False)
    consent_marketing = db.Column(db.Boolean, default=False)
    government_id_type = db.Column(db.String(40), nullable=True)
    government_id_number = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user         = db.relationship('User', back_populates='patient')
    appointments = db.relationship('Appointment', back_populates='patient')
    follow_ups   = db.relationship('FollowUp', back_populates='patient')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @staticmethod
    def generate_patient_uid(year=None):
        yy = year or datetime.utcnow().strftime('%y')
        prefix = f'CS{yy}P'
        last = Patient.query.filter(Patient.patient_uid.like(f'{prefix}%')) \
            .order_by(Patient.patient_uid.desc()) \
            .first()
        if last and last.patient_uid and last.patient_uid[-4:].isdigit():
            next_seq = int(last.patient_uid[-4:]) + 1
        else:
            next_seq = 1
        return f'{prefix}{next_seq:04d}'


class Department(db.Model):
    __tablename__ = 'departments'

    id             = db.Column(db.Integer, primary_key=True)
    department_uid = db.Column(db.String(20), unique=True, nullable=True)
    name           = db.Column(db.String(100), unique=True, nullable=False)
    description    = db.Column(db.Text, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    doctors        = db.relationship('Doctor', back_populates='department')

    @staticmethod
    def generate_department_uid():
        prefix = 'CSDE'
        last = Department.query.filter(Department.department_uid.like(f'{prefix}%')) \
            .order_by(Department.department_uid.desc()) \
            .first()
        if last and last.department_uid and last.department_uid[-3:].isdigit():
            next_seq = int(last.department_uid[-3:]) + 1
        else:
            next_seq = 1
        return f'{prefix}{next_seq:03d}'


class Doctor(db.Model):
    __tablename__ = 'doctors'

    id               = db.Column(db.Integer, primary_key=True)
    doctor_uid       = db.Column(db.String(20), unique=True, nullable=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name             = db.Column(db.String(120), nullable=False)
    gender           = db.Column(db.String(20), nullable=True)
    specialization   = db.Column(db.String(100), nullable=False)
    sub_specialties  = db.Column(db.Text, nullable=True)
    average_rating   = db.Column(db.Float, nullable=True)
    department_id    = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    qualification    = db.Column(db.String(200), nullable=True)
    languages_spoken = db.Column(db.Text, nullable=True)
    certifications   = db.Column(db.Text, nullable=True)
    awards           = db.Column(db.Text, nullable=True)
    past_experience  = db.Column(db.Text, nullable=True)
    appointment_fee  = db.Column(db.Float, nullable=True)
    experience_years = db.Column(db.Integer, default=0)
    bio              = db.Column(db.Text, nullable=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    user         = db.relationship('User', back_populates='doctor')
    department   = db.relationship('Department', back_populates='doctors')
    appointments = db.relationship('Appointment', back_populates='doctor')
    availability = db.relationship('DoctorAvailability', back_populates='doctor')
    follow_ups   = db.relationship('FollowUp', back_populates='doctor')

    @staticmethod
    def generate_doctor_uid(year=None):
        yy = year or datetime.utcnow().strftime('%y')
        prefix = f'CS{yy}D'
        last = Doctor.query.filter(Doctor.doctor_uid.like(f'{prefix}%')) \
            .order_by(Doctor.doctor_uid.desc()) \
            .first()
        if last and last.doctor_uid and last.doctor_uid[-4:].isdigit():
            next_seq = int(last.doctor_uid[-4:]) + 1
        else:
            next_seq = 1
        return f'{prefix}{next_seq:04d}'


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id             = db.Column(db.Integer, primary_key=True)
    appointment_uid = db.Column(db.String(20), unique=True, index=True, nullable=True)
    doctor_id      = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    patient_id     = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_dt = db.Column(db.DateTime, nullable=False)
    status         = db.Column(db.String(20), default='booked')
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    doctor  = db.relationship('Doctor', back_populates='appointments')
    patient = db.relationship('Patient', back_populates='appointments')
    treatment = db.relationship('Treatment', back_populates='appointment', uselist=False)

    @staticmethod
    def format_appointment_uid(appointment_id, year=None):
        yy = year or datetime.utcnow().strftime('%y')
        return f'CS{yy}A{int(appointment_id):04d}'


class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availability'

    id             = db.Column(db.Integer, primary_key=True)
    doctor_id      = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    available_date = db.Column(db.Date, nullable=False)
    start_time     = db.Column(db.String(5), nullable=False)   # "HH:MM"
    end_time       = db.Column(db.String(5), nullable=False)   # "HH:MM"
    max_slots      = db.Column(db.Integer, default=10)

    doctor = db.relationship('Doctor', back_populates='availability')


class Treatment(db.Model):
    __tablename__ = 'treatments'

    id             = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False, unique=True)
    diagnosis      = db.Column(db.Text, nullable=True)
    prescription   = db.Column(db.Text, nullable=True)
    notes          = db.Column(db.Text, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship('Appointment', back_populates='treatment')


class FollowUp(db.Model):
    """
    Doctor-scheduled follow-up after a visit (linked to source appointment).
    status: pending -> missed (after due_date) or booked (patient booked a follow-up visit).
    """
    __tablename__ = 'follow_ups'

    id                         = db.Column(db.Integer, primary_key=True)
    source_appointment_id      = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False, unique=True)
    patient_id                 = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id                  = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    due_date                   = db.Column(db.Date, nullable=False)
    days_interval              = db.Column(db.Integer, nullable=True)
    status                     = db.Column(db.String(20), nullable=False, default='pending')
    fulfilled_appointment_id   = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    created_at                 = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', back_populates='follow_ups')
    doctor  = db.relationship('Doctor', back_populates='follow_ups')
    source_appointment = db.relationship(
        'Appointment',
        foreign_keys=[source_appointment_id],
        backref=db.backref('scheduled_follow_up', uselist=False)
    )
    fulfilled_appointment = db.relationship('Appointment', foreign_keys=[fulfilled_appointment_id])


class ExportJob(db.Model):
    __tablename__ = 'export_jobs'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='queued')  # queued | processing | completed | failed
    record_count = db.Column(db.Integer, nullable=True)
    file_path = db.Column(db.Text, nullable=True)
    error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)


class MonthlyReport(db.Model):
    __tablename__ = 'monthly_reports'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    report_month = db.Column(db.String(20), nullable=False)   # e.g., "April 2026"
    file_path = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship('Doctor', backref=db.backref('monthly_reports', lazy=True))
