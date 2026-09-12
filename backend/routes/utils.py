from datetime import datetime, timedelta, date

def parse_dt(value: str):
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def appointment_to_dict(appt):
    row = {
        "id": appt.id,
        "appointment_uid": appt.appointment_uid,
        "doctor_id": appt.doctor_id,
        "doctor_uid": appt.doctor.doctor_uid if appt.doctor else None,
        "patient_id": appt.patient_id,
        "appointment_dt": appt.appointment_dt.isoformat(timespec="minutes"),
        "status": appt.status,
        "doctor_name": appt.doctor.name if appt.doctor else None,
        "doctor_specialization": appt.doctor.specialization if appt.doctor else None,
        "patient_name": appt.patient.full_name if appt.patient else None,
        "patient_uid": appt.patient.patient_uid if appt.patient else None,
        "patient_gender": appt.patient.gender if appt.patient else None,
        "patient_dob": appt.patient.dob.isoformat() if appt.patient and appt.patient.dob else None,
        "treatment": {
            "diagnosis": appt.treatment.diagnosis,
            "prescription": appt.treatment.prescription,
            "notes": appt.treatment.notes,
        } if appt.treatment else None,
    }
    fu = getattr(appt, "scheduled_follow_up", None)
    if fu:
        row["follow_up"] = {
            "id": fu.id,
            "due_date": fu.due_date.isoformat() if fu.due_date else None,
            "days_interval": fu.days_interval,
            "status": fu.status,
        }
    else:
        row["follow_up"] = None
    return row


def doctor_to_dict(doc):
    return {
        "id": doc.id,
        "doctor_uid": doc.doctor_uid,
        "name": doc.name,
        "gender": doc.gender,
        "specialization": doc.specialization,
        "sub_specialties": doc.sub_specialties,
        "department_id": doc.department_id,
        "department": doc.department.name if doc.department else None,
        "experience_years": doc.experience_years,
        "qualification": doc.qualification,
        "languages_spoken": doc.languages_spoken,
        "certifications": doc.certifications,
        "awards": doc.awards,
        "past_experience": doc.past_experience,
        "appointment_fee": doc.appointment_fee,
        "bio": doc.bio,
        "email": doc.user.email if doc.user else None,
        "is_blacklisted": doc.user.is_blacklisted if doc.user else False
    }


def follow_up_to_dict(fu, today=None):
    """Serialize FollowUp for patient dashboard (countdown, can_book, missed)."""
    today = today or date.today()
    delta_days = (fu.due_date - today).days
    # Book enabled from one calendar day before due date through until fulfilled
    book_from = fu.due_date - timedelta(days=1)
    can_book = fu.status in ('pending', 'missed') and today >= book_from
    return {
        'id': fu.id,
        'source_appointment_id': fu.source_appointment_id,
        'doctor_id': fu.doctor_id,
        'doctor_name': fu.doctor.name if fu.doctor else None,
        'due_date': fu.due_date.isoformat(),
        'days_interval': fu.days_interval,
        'status': fu.status,
        'days_until_due': delta_days,
        'can_book': can_book,
        'is_missed': fu.status == 'missed',
    }


def patient_to_dict(p):
    return {
        "id": p.id,
        "patient_uid": p.patient_uid,
        "first_name": p.first_name,
        "last_name": p.last_name,
        "full_name": p.full_name,
        "email": p.user.email if p.user else None,
        "phone": p.phone,
        "gender": p.gender,
        "dob": p.dob.isoformat() if p.dob else None,
        "address": p.address,
        "emergency_contact_name": p.emergency_contact_name,
        "emergency_contact_relationship": p.emergency_contact_relationship,
        "emergency_contact_phone": p.emergency_contact_phone,
        "insurance_provider": p.insurance_provider,
        "insurance_policy_number": p.insurance_policy_number,
        "insurance_member_id": p.insurance_member_id,
        "insurance_coverage_start": p.insurance_coverage_start.isoformat() if p.insurance_coverage_start else None,
        "allergies": p.allergies,
        "medications": p.medications,
        "conditions": p.conditions,
        "primary_physician": p.primary_physician,
        "preferred_language": p.preferred_language,
        "communication_preferences": p.communication_preferences,
        "accessibility_needs": p.accessibility_needs,
        "occupation": p.occupation,
        "marital_status": p.marital_status,
        "blood_type": p.blood_type,
        "family_history": p.family_history,
        "pregnancy_status": p.pregnancy_status,
        "preferred_pharmacy": p.preferred_pharmacy,
        "consent_terms": p.consent_terms,
        "consent_telehealth": p.consent_telehealth,
        "consent_reminders": p.consent_reminders,
        "consent_marketing": p.consent_marketing,
        "government_id_type": p.government_id_type,
        "government_id_number": p.government_id_number,
        "is_blacklisted": p.user.is_blacklisted if p.user else False,
        "created_at": p.created_at.isoformat() if p.created_at else None
    }


def department_to_dict(d):
    return {
        "id": d.id,
        "department_uid": d.department_uid,
        "name": d.name,
        "description": d.description,
        "doctor_count": len(d.doctors or [])
    }


def availability_to_dict(a):
    return {
        "id": a.id,
        "doctor_id": a.doctor_id,
        "available_date": a.available_date.isoformat(),
        "start_time": a.start_time,
        "end_time": a.end_time,
    }

def monthly_report_to_dict(report):
    return {
        "id": report.id,
        "doctor_id": report.doctor_id,
        "report_month": report.report_month,
        "file_path": report.file_path,
        "generated_at": report.generated_at.isoformat() if report.generated_at else None,
        "doctor_name": report.doctor.name if report.doctor else None,
    }
