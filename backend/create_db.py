"""
create_db.py — run once to initialise the database and seed the admin user.
Usage (recommended):  python3 -m backend.create_db
"""
from werkzeug.security import generate_password_hash

from .app import create_app
from .models import db, User, Department, Doctor, Patient, Appointment
from datetime import datetime, timedelta, date

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@hospital.local"
ADMIN_PASSWORD = "Admin@1234"  # change before deployment

# Dev seed users (for local demo/testing)
DOCTOR_EMAIL = "doctor@hospital.local"
DOCTOR_PASSWORD = "Doctor@1234"
PATIENT_EMAIL = "patient@hospital.local"
PATIENT_PASSWORD = "Patient@1234"

SEED_DEPARTMENTS = [
    ("Cardiology", "Heart and cardiovascular system"),
    ("Neurology", "Brain and nervous system"),
    ("Orthopedics", "Bones and joints"),
    ("Dermatology", "Skin, hair, and nail disorders"),
    ("Pediatrics", "Healthcare for children"),
    ("Gynecology & Obstetrics", "Women's health and pregnancy care"),
    ("Oncology", "Cancer diagnosis and treatment"),
    ("ENT (Otolaryngology)", "Ear, nose, and throat care"),
    ("Ophthalmology", "Eye care and vision health"),
    ("Urology", "Urinary system care"),
    ("Gastroenterology", "Digestive system care"),
    ("Endocrinology", "Hormone-related conditions"),
    ("Pulmonology", "Lung and respiratory care"),
    ("Nephrology", "Kidney care"),
    ("Psychiatry", "Mental health care"),
    ("General Surgery", "Surgical care for general conditions"),
    ("Plastic Surgery", "Reconstructive and cosmetic surgery"),
    ("Radiology", "Medical imaging and diagnostics"),
    ("Anesthesiology", "Anesthesia and perioperative care"),
    ("Emergency Medicine", "Emergency and urgent care"),
]


def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("[✓] Tables created.")

        # ── Admin ──────────────────────────────────────────────
        if not User.query.filter_by(role="admin").first():
            admin = User(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                password_hash=generate_password_hash(ADMIN_PASSWORD),
                role="admin",
                is_active=True,
            )
            db.session.add(admin)
            print(f"[✓] Admin user created  ({ADMIN_USERNAME} / {ADMIN_PASSWORD})")
        else:
            print("[–] Admin already exists, skipping.")

        # ── Departments ────────────────────────────────────────
        for name, desc in SEED_DEPARTMENTS:
            if not Department.query.filter_by(name=name).first():
                db.session.add(
                    Department(
                        department_uid=Department.generate_department_uid(),
                        name=name,
                        description=desc
                    )
                )
        db.session.commit()
        print(f"[✓] {len(SEED_DEPARTMENTS)} departments seeded.")

        # ── Doctor (dev seed) ─────────────────────────────────
        if not User.query.filter_by(email=DOCTOR_EMAIL).first():
            d_user = User(
                email=DOCTOR_EMAIL,
                password_hash=generate_password_hash(DOCTOR_PASSWORD),
                role="doctor",
                is_active=True,
            )
            db.session.add(d_user)
            db.session.flush()
            cardiology = Department.query.filter_by(name="Cardiology").first()
            doctor = Doctor(
                doctor_uid=Doctor.generate_doctor_uid(),
                user_id=d_user.id,
                name="Dr. Sarah Johnson",
                specialization="Cardiology",
                department_id=cardiology.id if cardiology else None,
                qualification="MD, Cardiology",
                experience_years=8,
            )
            db.session.add(doctor)
            db.session.commit()
            print(f"[✓] Doctor seeded ({DOCTOR_EMAIL} / {DOCTOR_PASSWORD})")
        else:
            doctor = Doctor.query.join(User).filter(User.email == DOCTOR_EMAIL).first()

        # ── Patient (dev seed) ────────────────────────────────
        if not User.query.filter_by(email=PATIENT_EMAIL).first():
            p_user = User(
                email=PATIENT_EMAIL,
                password_hash=generate_password_hash(PATIENT_PASSWORD),
                role="patient",
                is_active=True,
            )
            db.session.add(p_user)
            db.session.flush()
            patient = Patient(
                user_id=p_user.id,
                patient_uid=Patient.generate_patient_uid(),
                first_name="Emily",
                last_name="Chen",
                phone="+91 90000 00001",
                dob=date(1984, 5, 14),
                gender="Female",
                consent_terms=True,
            )
            db.session.add(patient)
            db.session.commit()
            print(f"[✓] Patient seeded ({PATIENT_EMAIL} / {PATIENT_PASSWORD})")
        else:
            patient = Patient.query.join(User).filter(User.email == PATIENT_EMAIL).first()

        # ── Appointments (dev seed) ───────────────────────────
        if doctor and patient:
            existing = Appointment.query.filter_by(doctor_id=doctor.id, patient_id=patient.id).count()
            if existing == 0:
                now = datetime.utcnow()
                base = datetime(now.year, now.month, now.day, 9, 0, 0)
                appts = [
                    Appointment(doctor_id=doctor.id, patient_id=patient.id, appointment_dt=base + timedelta(hours=0), status="booked"),
                    Appointment(doctor_id=doctor.id, patient_id=patient.id, appointment_dt=base + timedelta(hours=1), status="booked"),
                    Appointment(doctor_id=doctor.id, patient_id=patient.id, appointment_dt=base + timedelta(days=1, hours=2), status="booked"),
                ]
                db.session.add_all(appts)
                db.session.flush()
                for appt in appts:
                    year_tag = appt.appointment_dt.strftime('%y') if appt.appointment_dt else None
                    appt.appointment_uid = Appointment.format_appointment_uid(appt.id, year_tag)
                db.session.commit()
                print("[✓] Sample appointments seeded.")


if __name__ == "__main__":
    init_db()
