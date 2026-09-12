"""
seed_data.py
Database Seeding Script for CareSync Hospital Management System.
Populates realistic mock data across all tables, roles, and relationships.
Usage: python seed_data.py
"""

import sys
import os
import shutil
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import create_app
from backend.models import (
    db, User, Department, Doctor, Patient, Appointment,
    DoctorAvailability, Treatment, FollowUp, ExportJob, MonthlyReport
)

# ── Primary Demo Credentials ──────────────────────────────────────────
ADMIN_USER = "admin"
ADMIN_EMAIL = "admin@hospital.local"
ADMIN_PASS = "Admin@1234"

DOCTOR_EMAIL = "doctor@hospital.local"
DOCTOR_PASS = "Doctor@1234"

PATIENT_EMAIL = "patient@hospital.local"
PATIENT_PASS = "Patient@1234"


def seed():
    app = create_app()
    with app.app_context():
        print("[*] Resetting database tables...")
        db.drop_all()
        db.create_all()
        print("[✓] Clean database schema created.")

        # 1. ── Create Departments ─────────────────────────────────────
        departments_data = [
            ("Cardiology", "Comprehensive cardiovascular care, ECG, echo, and hypertension management"),
            ("Neurology", "Advanced brain, spine, stroke, and neuromuscular disorder care"),
            ("Orthopedics", "Bone, joint replacement, sports injury, and trauma surgery"),
            ("Dermatology", "Clinical dermatology, skin cancer screening, and cosmetic treatments"),
            ("Pediatrics", "Neonatal, infant, child health care and immunization services"),
            ("Gynecology & Obstetrics", "Women's wellness, prenatal, maternal, and reproductive care"),
            ("Oncology", "Medical, surgical, and radiation oncology treatment plans"),
            ("ENT (Otolaryngology)", "Ear, nose, throat, head and neck medical/surgical care"),
            ("Ophthalmology", "Vision health, cataract surgery, glaucoma management, and retina care"),
            ("Gastroenterology", "Digestive system, liver, endoscopy, and inflammatory bowel care"),
            ("Psychiatry", "Mental health, behavioral health, and psychiatric counseling"),
            ("General Surgery", "Minimally invasive, laparoscopic, and emergency surgical care"),
        ]

        dept_objs = {}
        for idx, (name, desc) in enumerate(departments_data, 1):
            dept = Department(
                department_uid=f"CSDE{idx:03d}",
                name=name,
                description=desc
            )
            db.session.add(dept)
            dept_objs[name] = dept
        
        db.session.commit()
        print(f"[✓] {len(dept_objs)} Departments created.")

        # 2. ── Create Admin User ──────────────────────────────────────
        admin_user = User(
            username=ADMIN_USER,
            email=ADMIN_EMAIL,
            password_hash=generate_password_hash(ADMIN_PASS),
            role="admin",
            is_active=True,
        )
        db.session.add(admin_user)
        print(f"[✓] Primary Admin created ({ADMIN_USER} / {ADMIN_PASS})")

        # 3. ── Create Primary Doctor & Additional Doctors ─────────────
        doctors_raw = [
            {
                "email": DOCTOR_EMAIL,
                "name": "Dr. Sarah Johnson",
                "gender": "Female",
                "dept_name": "Cardiology",
                "specialization": "Cardiology",
                "sub_specialties": "Interventional Cardiology, Heart Failure, Echocardiography",
                "average_rating": 4.9,
                "qualification": "MD (Cardiology), FACC",
                "languages_spoken": "English, Spanish",
                "certifications": "Board Certified Interventional Cardiologist",
                "awards": "Top Physician Award 2024, Excellence in Patient Care 2025",
                "past_experience": "10 years Senior Consultant at Johns Hopkins Hospital",
                "appointment_fee": 1200.0,
                "experience_years": 14,
                "bio": "Dr. Sarah Johnson specializes in preventative cardiology and complex cardiovascular intervention."
            },
            {
                "email": "dr.marcus.vance@hospital.local",
                "name": "Dr. Marcus Vance",
                "gender": "Male",
                "dept_name": "Neurology",
                "specialization": "Neurology",
                "sub_specialties": "Stroke Care, Multiple Sclerosis, Epilepsy",
                "average_rating": 4.8,
                "qualification": "MD, DM Neurology (Harvard Medical)",
                "languages_spoken": "English, French",
                "certifications": "American Board of Psychiatry and Neurology",
                "awards": "Neuroscience Pioneer Fellowship 2023",
                "past_experience": "8 years Lead Neurologist at Mass General",
                "appointment_fee": 1500.0,
                "experience_years": 12,
                "bio": "Expert in neurological disorders, stroke prevention, and cognitive health management."
            },
            {
                "email": "dr.priya.sharma@hospital.local",
                "name": "Dr. Priya Sharma",
                "gender": "Female",
                "dept_name": "Pediatrics",
                "specialization": "Pediatrics",
                "sub_specialties": "Pediatric Allergy, Neonatal Care, Growth & Development",
                "average_rating": 4.95,
                "qualification": "MBBS, DCH, MD (Pediatrics)",
                "languages_spoken": "English, Hindi, Punjabi",
                "certifications": "Certified Pediatrician (AAP)",
                "awards": "Compassionate Caregiver Award 2024",
                "past_experience": "9 years Senior Pediatric Consultant",
                "appointment_fee": 900.0,
                "experience_years": 11,
                "bio": "Dedicated to comprehensive child health, developmental milestones, and pediatric wellness."
            },
            {
                "email": "dr.robert.chen@hospital.local",
                "name": "Dr. Robert Chen",
                "gender": "Male",
                "dept_name": "Orthopedics",
                "specialization": "Orthopedics",
                "sub_specialties": "Joint Replacement, Arthroscopy, Sports Medicine",
                "average_rating": 4.7,
                "qualification": "MS (Orthopedics), FRCS",
                "languages_spoken": "English, Mandarin",
                "certifications": "Board Certified Orthopedic Surgeon",
                "awards": "Surgical Innovation Medal 2023",
                "past_experience": "15 years Orthopedic Surgeon at Mayo Clinic",
                "appointment_fee": 1400.0,
                "experience_years": 16,
                "bio": "Specialist in minimally invasive knee and hip joint replacement and sports injury recovery."
            },
            {
                "email": "dr.elena.rostova@hospital.local",
                "name": "Dr. Elena Rostova",
                "gender": "Female",
                "dept_name": "Dermatology",
                "specialization": "Dermatology",
                "sub_specialties": "Cosmetic Dermatology, Psoriasis, Laser Therapy",
                "average_rating": 4.85,
                "qualification": "MD Dermatology, FAAD",
                "languages_spoken": "English, Russian",
                "certifications": "American Academy of Dermatology Fellow",
                "awards": "Dermatology Researcher of the Year 2024",
                "past_experience": "7 years Clinical Director at Skin & Laser Center",
                "appointment_fee": 1100.0,
                "experience_years": 9,
                "bio": "Provides expert medical and aesthetic dermatological treatments with personalized skin plans."
            },
            {
                "email": "dr.david.kim@hospital.local",
                "name": "Dr. David Kim",
                "gender": "Male",
                "dept_name": "Gastroenterology",
                "specialization": "Gastroenterology",
                "sub_specialties": "Hepatology, Advanced Endoscopy, IBS Management",
                "average_rating": 4.75,
                "qualification": "MD, FACG",
                "languages_spoken": "English, Korean",
                "certifications": "Board Certified Gastroenterologist",
                "awards": "Clinical Research Award 2023",
                "past_experience": "11 years Staff Gastroenterologist",
                "appointment_fee": 1300.0,
                "experience_years": 13,
                "bio": "Expert in diagnostic endoscopy, liver disease management, and digestive health."
            },
            {
                "email": "dr.aisha.khan@hospital.local",
                "name": "Dr. Aisha Khan",
                "gender": "Female",
                "dept_name": "Gynecology & Obstetrics",
                "specialization": "Gynecology & Obstetrics",
                "sub_specialties": "High-Risk Pregnancy, Laparoscopic Surgery, Infertility",
                "average_rating": 4.9,
                "qualification": "MD, FACOG",
                "languages_spoken": "English, Urdu, Arabic",
                "certifications": "Board Certified Obstetrician & Gynecologist",
                "awards": "Maternal Health Excellence Award 2025",
                "past_experience": "12 years Senior Ob/Gyn Specialist",
                "appointment_fee": 1250.0,
                "experience_years": 14,
                "bio": "Specialized in high-risk pregnancy care, robotic gynecological surgery, and women's health."
            },
            {
                "email": "dr.james.wilson@hospital.local",
                "name": "Dr. James Wilson",
                "gender": "Male",
                "dept_name": "Oncology",
                "specialization": "Oncology",
                "sub_specialties": "Medical Oncology, Immunotherapy, Breast Cancer",
                "average_rating": 4.92,
                "qualification": "MD, PhD (Oncology)",
                "languages_spoken": "English, German",
                "certifications": "ASCO Certified Medical Oncologist",
                "awards": "Cancer Research Chair 2024",
                "past_experience": "14 years Senior Oncologist at Memorial Sloan Kettering",
                "appointment_fee": 1800.0,
                "experience_years": 17,
                "bio": "Pioneer in targeted cancer therapies, clinical trial management, and holistic cancer care."
            }
        ]

        doctor_objs = []
        for d_idx, doc_data in enumerate(doctors_raw, 1):
            password = DOCTOR_PASS if doc_data["email"] == DOCTOR_EMAIL else "Doctor@1234"
            doc_user = User(
                email=doc_data["email"],
                password_hash=generate_password_hash(password),
                role="doctor",
                is_active=True
            )
            db.session.add(doc_user)
            db.session.flush()

            dept = dept_objs.get(doc_data["dept_name"])
            doctor = Doctor(
                doctor_uid=f"CS26D{d_idx:04d}",
                user_id=doc_user.id,
                name=doc_data["name"],
                gender=doc_data["gender"],
                specialization=doc_data["specialization"],
                sub_specialties=doc_data["sub_specialties"],
                average_rating=doc_data["average_rating"],
                department_id=dept.id if dept else None,
                qualification=doc_data["qualification"],
                languages_spoken=doc_data["languages_spoken"],
                certifications=doc_data["certifications"],
                awards=doc_data["awards"],
                past_experience=doc_data["past_experience"],
                appointment_fee=doc_data["appointment_fee"],
                experience_years=doc_data["experience_years"],
                bio=doc_data["bio"]
            )
            db.session.add(doctor)
            doctor_objs.append(doctor)
        
        db.session.commit()
        print(f"[✓] {len(doctor_objs)} Doctors seeded (Primary Doctor: {DOCTOR_EMAIL} / {DOCTOR_PASS}).")

        # 4. ── Create Primary Patient & Additional Patients ────────────
        patients_raw = [
            {
                "email": PATIENT_EMAIL,
                "first_name": "Emily",
                "last_name": "Chen",
                "phone": "+1 (555) 234-5678",
                "dob": date(1992, 5, 14),
                "gender": "Female",
                "address": "742 Evergreen Terrace, San Jose, CA",
                "emergency_contact_name": "David Chen",
                "emergency_contact_relationship": "Brother",
                "emergency_contact_phone": "+1 (555) 987-6543",
                "insurance_provider": "Blue Cross Blue Shield",
                "insurance_policy_number": "BCBS-889021",
                "insurance_member_id": "MEM-99201",
                "insurance_coverage_start": date(2022, 1, 1),
                "allergies": "Penicillin, Dust Mites",
                "medications": "Lisinopril 10mg daily, Multivitamins",
                "conditions": "Mild Hypertension, Seasonal Allergies",
                "primary_physician": "Dr. Sarah Johnson",
                "preferred_language": "English",
                "communication_preferences": "Email, SMS",
                "accessibility_needs": "None",
                "occupation": "Software Engineer",
                "marital_status": "Single",
                "blood_type": "A+",
                "family_history": "Maternal Type 2 Diabetes, Paternal Hypertension",
                "pregnancy_status": "Not Pregnant",
                "preferred_pharmacy": "Walgreens Pharmacy #4402",
                "government_id_type": "Passport",
                "government_id_number": "P88920194"
            },
            {
                "email": "michael.brown@example.com",
                "first_name": "Michael",
                "last_name": "Brown",
                "phone": "+1 (555) 345-6789",
                "dob": date(1985, 11, 22),
                "gender": "Male",
                "address": "1204 Pine Street, Seattle, WA",
                "emergency_contact_name": "Sarah Brown",
                "emergency_contact_relationship": "Spouse",
                "emergency_contact_phone": "+1 (555) 876-5432",
                "insurance_provider": "Aetna Health",
                "insurance_policy_number": "AET-554109",
                "insurance_member_id": "MEM-11029",
                "insurance_coverage_start": date(2021, 6, 15),
                "allergies": "Sulfa Drugs",
                "medications": "Metformin 500mg, Atorvastatin 20mg",
                "conditions": "Type 2 Diabetes, Hyperlipidemia",
                "primary_physician": "Dr. Marcus Vance",
                "preferred_language": "English",
                "communication_preferences": "SMS",
                "accessibility_needs": "None",
                "occupation": "Accountant",
                "marital_status": "Married",
                "blood_type": "O+",
                "family_history": "Paternal Coronary Artery Disease",
                "pregnancy_status": "N/A",
                "preferred_pharmacy": "CVS Health #1209",
                "government_id_type": "Driver License",
                "government_id_number": "DL-9920412"
            },
            {
                "email": "sophia.rodriguez@example.com",
                "first_name": "Sophia",
                "last_name": "Rodriguez",
                "phone": "+1 (555) 456-7890",
                "dob": date(1998, 3, 8),
                "gender": "Female",
                "address": "450 Ocean Drive, Miami, FL",
                "emergency_contact_name": "Maria Rodriguez",
                "emergency_contact_relationship": "Mother",
                "emergency_contact_phone": "+1 (555) 765-4321",
                "insurance_provider": "UnitedHealthcare",
                "insurance_policy_number": "UHC-771203",
                "insurance_member_id": "MEM-44912",
                "insurance_coverage_start": date(2023, 3, 1),
                "allergies": "Peanuts, Shellfish",
                "medications": "Albuterol Inhaler as needed",
                "conditions": "Mild Asthma",
                "primary_physician": "Dr. Priya Sharma",
                "preferred_language": "Spanish",
                "communication_preferences": "Email",
                "accessibility_needs": "None",
                "occupation": "Graphic Designer",
                "marital_status": "Single",
                "blood_type": "B+",
                "family_history": "Maternal Asthma",
                "pregnancy_status": "Not Pregnant",
                "preferred_pharmacy": "Publix Pharmacy #801",
                "government_id_type": "Driver License",
                "government_id_number": "DL-7730192"
            },
            {
                "email": "james.harrison@example.com",
                "first_name": "James",
                "last_name": "Harrison",
                "phone": "+1 (555) 567-8901",
                "dob": date(1974, 8, 30),
                "gender": "Male",
                "address": "890 Oak Ridge Rd, Chicago, IL",
                "emergency_contact_name": "Laura Harrison",
                "emergency_contact_relationship": "Wife",
                "emergency_contact_phone": "+1 (555) 654-3210",
                "insurance_provider": "Cigna Healthcare",
                "insurance_policy_number": "CGN-334912",
                "insurance_member_id": "MEM-66301",
                "insurance_coverage_start": date(2020, 9, 1),
                "allergies": "Latex, Iodine",
                "medications": "Omeprazole 20mg, Aspirin 81mg",
                "conditions": "GERD, Osteoarthritis (Right Knee)",
                "primary_physician": "Dr. Robert Chen",
                "preferred_language": "English",
                "communication_preferences": "Phone Call, Email",
                "accessibility_needs": "Wheelchair Access Ramp Required",
                "occupation": "Civil Engineer",
                "marital_status": "Married",
                "blood_type": "O-",
                "family_history": "Arthritis, Gout",
                "pregnancy_status": "N/A",
                "preferred_pharmacy": "Walgreens #1029",
                "government_id_type": "Passport",
                "government_id_number": "P3391024"
            },
            {
                "email": "ananya.patel@example.com",
                "first_name": "Ananya",
                "last_name": "Patel",
                "phone": "+1 (555) 678-9012",
                "dob": date(2001, 12, 5),
                "gender": "Female",
                "address": "332 College Ave, Austin, TX",
                "emergency_contact_name": "Rajesh Patel",
                "emergency_contact_relationship": "Father",
                "emergency_contact_phone": "+1 (555) 543-2109",
                "insurance_provider": "Kaiser Permanente",
                "insurance_policy_number": "KP-991204",
                "insurance_member_id": "MEM-88392",
                "insurance_coverage_start": date(2024, 1, 15),
                "allergies": "None Known",
                "medications": "Oral Contraceptive Pill",
                "conditions": "Eczema",
                "primary_physician": "Dr. Elena Rostova",
                "preferred_language": "English, Gujarati",
                "communication_preferences": "SMS, Email",
                "accessibility_needs": "None",
                "occupation": "Graduate Student",
                "marital_status": "Single",
                "blood_type": "AB+",
                "family_history": "Eczema, Thyroid Disorder",
                "pregnancy_status": "Not Pregnant",
                "preferred_pharmacy": "H-E-B Pharmacy #302",
                "government_id_type": "State ID",
                "government_id_number": "TX-4402194"
            },
            {
                "email": "david.miller@example.com",
                "first_name": "David",
                "last_name": "Miller",
                "phone": "+1 (555) 789-0123",
                "dob": date(1968, 4, 17),
                "gender": "Male",
                "address": "512 Highland Ave, Denver, CO",
                "emergency_contact_name": "Karen Miller",
                "emergency_contact_relationship": "Sister",
                "emergency_contact_phone": "+1 (555) 432-1098",
                "insurance_provider": "Humana",
                "insurance_policy_number": "HUM-448201",
                "insurance_member_id": "MEM-22910",
                "insurance_coverage_start": date(2019, 4, 1),
                "allergies": "Codeine",
                "medications": "Levothyroxine 75mcg, Amlodipine 5mg",
                "conditions": "Hypothyroidism, Hypertension",
                "primary_physician": "Dr. David Kim",
                "preferred_language": "English",
                "communication_preferences": "Phone Call",
                "accessibility_needs": "Hearing Assistance",
                "occupation": "Architect",
                "marital_status": "Divorced",
                "blood_type": "A-",
                "family_history": "Thyroid Cancer, Stroke",
                "pregnancy_status": "N/A",
                "preferred_pharmacy": "Safeway Pharmacy #504",
                "government_id_type": "Driver License",
                "government_id_number": "DL-110294"
            }
        ]

        patient_objs = []
        for p_idx, pat_data in enumerate(patients_raw, 1):
            password = PATIENT_PASS if pat_data["email"] == PATIENT_EMAIL else "Patient@1234"
            p_user = User(
                email=pat_data["email"],
                password_hash=generate_password_hash(password),
                role="patient",
                is_active=True
            )
            db.session.add(p_user)
            db.session.flush()

            patient = Patient(
                patient_uid=f"CS26P{p_idx:04d}",
                user_id=p_user.id,
                first_name=pat_data["first_name"],
                last_name=pat_data["last_name"],
                phone=pat_data["phone"],
                dob=pat_data["dob"],
                gender=pat_data["gender"],
                address=pat_data["address"],
                emergency_contact_name=pat_data["emergency_contact_name"],
                emergency_contact_relationship=pat_data["emergency_contact_relationship"],
                emergency_contact_phone=pat_data["emergency_contact_phone"],
                insurance_provider=pat_data["insurance_provider"],
                insurance_policy_number=pat_data["insurance_policy_number"],
                insurance_member_id=pat_data["insurance_member_id"],
                insurance_coverage_start=pat_data["insurance_coverage_start"],
                allergies=pat_data["allergies"],
                medications=pat_data["medications"],
                conditions=pat_data["conditions"],
                primary_physician=pat_data["primary_physician"],
                preferred_language=pat_data["preferred_language"],
                communication_preferences=pat_data["communication_preferences"],
                accessibility_needs=pat_data["accessibility_needs"],
                occupation=pat_data["occupation"],
                marital_status=pat_data["marital_status"],
                blood_type=pat_data["blood_type"],
                family_history=pat_data["family_history"],
                pregnancy_status=pat_data["pregnancy_status"],
                preferred_pharmacy=pat_data["preferred_pharmacy"],
                consent_terms=True,
                consent_telehealth=True,
                consent_reminders=True,
                consent_marketing=False,
                government_id_type=pat_data["government_id_type"],
                government_id_number=pat_data["government_id_number"]
            )
            db.session.add(patient)
            patient_objs.append(patient)
        
        db.session.commit()
        print(f"[✓] {len(patient_objs)} Patients seeded (Primary Patient: {PATIENT_EMAIL} / {PATIENT_PASS}).")

        # 5. ── Doctor Availability Slots ──────────────────────────────
        today = date.today()
        avail_objs = []
        for doc in doctor_objs:
            for day_offset in range(0, 14):
                slot_date = today + timedelta(days=day_offset)
                if slot_date.weekday() < 5:  # Monday to Friday
                    avail = DoctorAvailability(
                        doctor_id=doc.id,
                        available_date=slot_date,
                        start_time="09:00",
                        end_time="17:00",
                        max_slots=10
                    )
                    db.session.add(avail)
                    avail_objs.append(avail)
        db.session.commit()
        print(f"[✓] {len(avail_objs)} Doctor Availability slots seeded.")

        # 6. ── Appointments & Treatments & FollowUps ──────────────────
        now = datetime.utcnow()
        appointments_spec = [
            # Past Completed Appointments
            {"doc": doctor_objs[0], "pat": patient_objs[0], "days_offset": -15, "hour": 10, "status": "completed", "diagnosis": "Essential Hypertension (ICD-10 I10)", "prescription": "1. Lisinopril 10mg PO QD\n2. Hydrochlorothiazide 12.5mg PO QD", "notes": "BP controlled at 128/82 mmHg. Continue current regimen."},
            {"doc": doctor_objs[0], "pat": patient_objs[1], "days_offset": -10, "hour": 11, "status": "completed", "diagnosis": "Hyperlipidemia & Coronary Risk Screening", "prescription": "1. Atorvastatin 20mg PO QHS\n2. Low-salt diet plan", "notes": "Lipid panel shows LDL 142. Statins started. Follow up in 30 days."},
            {"doc": doctor_objs[1], "pat": patient_objs[1], "days_offset": -8, "hour": 14, "status": "completed", "diagnosis": "Tension Headache & Work-related Neck Strain", "prescription": "1. Acetaminophen 500mg PO PRN\n2. Physical Therapy 2x/week", "notes": "Cervical spine X-ray normal. Recommended ergonomic chair and PT."},
            {"doc": doctor_objs[2], "pat": patient_objs[2], "days_offset": -7, "hour": 9, "status": "completed", "diagnosis": "Acute Bronchial Asthma Exacerbation", "prescription": "1. Albuterol MDI 2 puffs Q4H PRN\n2. Prednisolone 20mg PO QD x 5 days", "notes": "Lungs clear post-nebulization. Patient educated on inhaler technique."},
            {"doc": doctor_objs[3], "pat": patient_objs[3], "days_offset": -5, "hour": 15, "status": "completed", "diagnosis": "Osteoarthritis of Right Knee (Grade II)", "prescription": "1. Celecoxib 100mg PO BID\n2. Glucosamine Supplement 1500mg QD", "notes": "Right knee joint space narrowing noted on X-ray. Intra-articular injection discussed."},
            {"doc": doctor_objs[4], "pat": patient_objs[4], "days_offset": -4, "hour": 16, "status": "completed", "diagnosis": "Atopic Dermatitis & Contact Eczema", "prescription": "1. Hydrocortisone 1% Ointment BID\n2. Cetaphil Moisturizing Cream QD", "notes": "Erythematous patches on flexor surfaces. Recommended fragrance-free soaps."},
            
            # Today's Booked Appointments
            {"doc": doctor_objs[0], "pat": patient_objs[0], "days_offset": 0, "hour": 9, "status": "booked", "diagnosis": None, "prescription": None, "notes": None},
            {"doc": doctor_objs[0], "pat": patient_objs[2], "days_offset": 0, "hour": 11, "status": "booked", "diagnosis": None, "prescription": None, "notes": None},
            {"doc": doctor_objs[1], "pat": patient_objs[3], "days_offset": 0, "hour": 14, "status": "booked", "diagnosis": None, "prescription": None, "notes": None},
            {"doc": doctor_objs[2], "pat": patient_objs[4], "days_offset": 0, "hour": 15, "status": "booked", "diagnosis": None, "prescription": None, "notes": None},
            {"doc": doctor_objs[5], "pat": patient_objs[5], "days_offset": 0, "hour": 16, "status": "booked", "diagnosis": None, "prescription": None, "notes": None},

            # Upcoming Booked Appointments
            {"doc": doctor_objs[0], "pat": patient_objs[1], "days_offset": 2, "hour": 10, "status": "booked", "diagnosis": None, "prescription": None, "notes": None},
            {"doc": doctor_objs[1], "pat": patient_objs[0], "days_offset": 3, "hour": 11, "status": "booked", "diagnosis": None, "prescription": None, "notes": None},
            {"doc": doctor_objs[3], "pat": patient_objs[3], "days_offset": 4, "hour": 14, "status": "booked", "diagnosis": None, "prescription": None, "notes": None},
            {"doc": doctor_objs[4], "pat": patient_objs[4], "days_offset": 5, "hour": 10, "status": "booked", "diagnosis": None, "prescription": None, "notes": None},
            {"doc": doctor_objs[6], "pat": patient_objs[2], "days_offset": 6, "hour": 15, "status": "booked", "diagnosis": None, "prescription": None, "notes": None},
            {"doc": doctor_objs[7], "pat": patient_objs[5], "days_offset": 7, "hour": 9, "status": "booked", "diagnosis": None, "prescription": None, "notes": None},

            # Cancelled Appointments
            {"doc": doctor_objs[0], "pat": patient_objs[4], "days_offset": -2, "hour": 13, "status": "cancelled", "diagnosis": None, "prescription": None, "notes": None},
            {"doc": doctor_objs[2], "pat": patient_objs[1], "days_offset": -1, "hour": 12, "status": "cancelled", "diagnosis": None, "prescription": None, "notes": None},
        ]

        appts_created = []
        treatments_created = []
        followups_created = []

        for idx, spec in enumerate(appointments_spec, 1):
            appt_time = datetime(now.year, now.month, now.day, spec["hour"], 0, 0) + timedelta(days=spec["days_offset"])
            year_tag = appt_time.strftime('%y')

            appt = Appointment(
                doctor_id=spec["doc"].id,
                patient_id=spec["pat"].id,
                appointment_dt=appt_time,
                status=spec["status"]
            )
            db.session.add(appt)
            db.session.flush()

            appt.appointment_uid = Appointment.format_appointment_uid(appt.id, year_tag)
            appts_created.append(appt)

            # Add treatment if completed
            if spec["status"] == "completed" and spec["diagnosis"]:
                treat = Treatment(
                    appointment_id=appt.id,
                    diagnosis=spec["diagnosis"],
                    prescription=spec["prescription"],
                    notes=spec["notes"],
                    created_at=appt_time + timedelta(minutes=30)
                )
                db.session.add(treat)
                treatments_created.append(treat)

                # Add scheduled follow-up
                due_d = appt_time.date() + timedelta(days=14)
                follow = FollowUp(
                    source_appointment_id=appt.id,
                    patient_id=spec["pat"].id,
                    doctor_id=spec["doc"].id,
                    due_date=due_d,
                    days_interval=14,
                    status="pending"
                )
                db.session.add(follow)
                followups_created.append(follow)

        db.session.commit()
        print(f"[✓] {len(appts_created)} Appointments, {len(treatments_created)} Treatments, and {len(followups_created)} Follow-ups created.")

        # 7. ── Export Jobs ────────────────────────────────────────────
        export_jobs_data = [
            {"pat": patient_objs[0], "status": "completed", "count": 14, "path": "exports/CS26P0001_health_records_2026.pdf"},
            {"pat": patient_objs[1], "status": "completed", "count": 22, "path": "exports/CS26P0002_health_records_2026.pdf"},
            {"pat": patient_objs[2], "status": "processing", "count": None, "path": None},
            {"pat": patient_objs[3], "status": "queued", "count": None, "path": None},
        ]
        for ej in export_jobs_data:
            job = ExportJob(
                patient_id=ej["pat"].id,
                status=ej["status"],
                record_count=ej["count"],
                file_path=ej["path"],
                created_at=now - timedelta(hours=2),
                completed_at=(now - timedelta(hours=1)) if ej["status"] == "completed" else None
            )
            db.session.add(job)
        
        # 8. ── Monthly Reports ────────────────────────────────────────
        reports_data = [
            {"doc": doctor_objs[0], "month": "March 2026", "path": "reports/CS26D0001_March_2026_Performance.pdf"},
            {"doc": doctor_objs[0], "month": "February 2026", "path": "reports/CS26D0001_February_2026_Performance.pdf"},
            {"doc": doctor_objs[1], "month": "March 2026", "path": "reports/CS26D0002_March_2026_Performance.pdf"},
            {"doc": doctor_objs[2], "month": "March 2026", "path": "reports/CS26D0003_March_2026_Performance.pdf"},
        ]
        for r in reports_data:
            rep = MonthlyReport(
                doctor_id=r["doc"].id,
                report_month=r["month"],
                file_path=r["path"],
                generated_at=now - timedelta(days=5)
            )
            db.session.add(rep)

        db.session.commit()

        # Copy database file to both instance paths so Flask and root tools match
        db_file = os.path.join(app.instance_path, 'hms.db')
        root_db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance', 'hms.db'))
        if os.path.exists(db_file) and db_file != root_db_file:
            os.makedirs(os.path.dirname(root_db_file), exist_ok=True)
            shutil.copy2(db_file, root_db_file)

        print("[✓] Export Jobs and Monthly Reports seeded.")
        print("\n========================================================")
        print("🎉 Database successfully seeded with rich, realistic mock data!")
        print("========================================================")
        print(f"  Admin Creds:    {ADMIN_USER} / {ADMIN_PASS}")
        print(f"  Doctor Creds:   {DOCTOR_EMAIL} / {DOCTOR_PASS}")
        print(f"  Patient Creds:  {PATIENT_EMAIL} / {PATIENT_PASS}")
        print("========================================================\n")


if __name__ == "__main__":
    seed()
