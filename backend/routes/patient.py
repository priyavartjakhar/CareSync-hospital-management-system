from flask import Blueprint, request, jsonify, Response, send_file
from datetime import datetime, timedelta, date
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import or_
import os

from ..models import (
    db,
    User,
    Patient,
    Doctor,
    Department,
    Appointment,
    DoctorAvailability,
    Treatment,
    FollowUp,
    ExportJob,
)
from ..auth.routes import token_required
from .utils import (
    appointment_to_dict,
    doctor_to_dict,
    department_to_dict,
    availability_to_dict,
    follow_up_to_dict,
    parse_dt,
)

patient_bp = Blueprint('patient', __name__)


def compute_slots_for_doctor_date(doctor_id: int, target_date: date):
    """
    Build 30-minute slot list for a doctor on a date (same rules as /available-slots).
    """
    avails = DoctorAvailability.query.filter_by(
        doctor_id=doctor_id,
        available_date=target_date
    ).order_by(DoctorAvailability.start_time).all()

    if not avails:
        return []

    day_start = datetime(target_date.year, target_date.month, target_date.day)
    day_end = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
    booked = {
        a.appointment_dt.strftime('%H:%M')
        for a in Appointment.query.filter_by(doctor_id=doctor_id, status='booked')
        .filter(Appointment.appointment_dt >= day_start)
        .filter(Appointment.appointment_dt <= day_end)
        .all()
    }

    slots = []
    seen = set()
    for a in avails:
        start_dt = datetime.combine(target_date, datetime.strptime(a.start_time, '%H:%M').time())
        end_dt = datetime.combine(target_date, datetime.strptime(a.end_time, '%H:%M').time())
        count = 0
        while start_dt < end_dt:
            t = start_dt.strftime('%H:%M')
            if t not in seen:
                slots.append({
                    'time': t,
                    'available': t not in booked
                })
                seen.add(t)
                count += 1
            start_dt = start_dt + timedelta(minutes=30)
            if a.max_slots and count >= a.max_slots:
                break

    slots.sort(key=lambda s: s['time'])
    return slots


def doctor_has_free_slot(doctor_id: int, target_date: date) -> bool:
    return any(s['available'] for s in compute_slots_for_doctor_date(doctor_id, target_date))


def is_strong_password(password: str) -> bool:
    pwd = str(password or '')
    return (
        len(pwd) >= 8
        and any(c.islower() for c in pwd)
        and any(c.isupper() for c in pwd)
        and any(c.isdigit() for c in pwd)
        and any(not c.isalnum() for c in pwd)
    )


@patient_bp.route('/profile', methods=['GET', 'PUT'])
@token_required(roles=['patient'])
def profile(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'Patient profile not found'}), 404

    if request.method == 'PUT':
        data = request.get_json() or {}
        email = data.get('email')
        if email is not None:
            normalized_email = email.strip().lower()
            if not normalized_email:
                return jsonify({'message': 'Email cannot be empty.'}), 400
            existing_user = User.query.filter(
                User.email == normalized_email,
                User.id != current_user.id
            ).first()
            if existing_user:
                return jsonify({'message': 'An account with this email already exists.'}), 409
            current_user.email = normalized_email

        incoming_phone = data.get('phone')
        if incoming_phone is not None:
            incoming_phone = incoming_phone.strip()
            if not incoming_phone:
                return jsonify({'message': 'Phone number cannot be empty.'}), 400
            phone_owner = Patient.query.filter(
                Patient.phone == incoming_phone,
                Patient.id != patient.id
            ).first()
            if phone_owner:
                return jsonify({'message': 'An account with this phone number already exists.'}), 409
            patient.phone = incoming_phone

        current_password = data.get('current_password')
        new_password = data.get('new_password')
        if current_password is not None or new_password is not None:
            if not current_password or not new_password:
                return jsonify({'message': 'Both current_password and new_password are required to change password.'}), 400
            if not is_strong_password(new_password):
                return jsonify({
                    'message': 'New password must be 8+ chars and include uppercase, lowercase, number, and special character.'
                }), 400
            if not check_password_hash(current_user.password_hash, current_password):
                return jsonify({'message': 'Current password is incorrect.'}), 400
            current_user.password_hash = generate_password_hash(new_password)

        for field in (
            'first_name',
            'last_name',
            'gender',
            'address',
            'emergency_contact_name',
            'emergency_contact_relationship',
            'emergency_contact_phone',
            'insurance_provider',
            'insurance_policy_number',
            'insurance_member_id',
            'allergies',
            'medications',
            'conditions',
            'primary_physician',
            'preferred_language',
            'communication_preferences',
            'accessibility_needs',
            'occupation',
            'marital_status',
            'blood_type',
            'family_history',
            'pregnancy_status',
            'preferred_pharmacy',
            'consent_terms',
            'consent_telehealth',
            'consent_reminders',
            'consent_marketing',
            'government_id_type',
            'government_id_number',
        ):
            if field in data:
                setattr(patient, field, data[field])
        if 'dob' in data:
            patient.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        if 'insurance_coverage_start' in data and data['insurance_coverage_start']:
            patient.insurance_coverage_start = datetime.strptime(
                data['insurance_coverage_start'],
                '%Y-%m-%d'
            ).date()
        elif 'insurance_coverage_start' in data:
            patient.insurance_coverage_start = None
        db.session.commit()

    return jsonify({
        'id': patient.id,
        'patient_uid': patient.patient_uid,
        'first_name': patient.first_name,
        'last_name': patient.last_name,
        'email': current_user.email,
        'phone': patient.phone,
        'dob': patient.dob.isoformat() if patient.dob else None,
        'gender': patient.gender,
        'address': patient.address,
        'emergency_contact_name': patient.emergency_contact_name,
        'emergency_contact_relationship': patient.emergency_contact_relationship,
        'emergency_contact_phone': patient.emergency_contact_phone,
        'insurance_provider': patient.insurance_provider,
        'insurance_policy_number': patient.insurance_policy_number,
        'insurance_member_id': patient.insurance_member_id,
        'insurance_coverage_start': patient.insurance_coverage_start.isoformat() if patient.insurance_coverage_start else None,
        'allergies': patient.allergies,
        'medications': patient.medications,
        'conditions': patient.conditions,
        'primary_physician': patient.primary_physician,
        'preferred_language': patient.preferred_language,
        'communication_preferences': patient.communication_preferences,
        'accessibility_needs': patient.accessibility_needs,
        'occupation': patient.occupation,
        'marital_status': patient.marital_status,
        'blood_type': patient.blood_type,
        'family_history': patient.family_history,
        'pregnancy_status': patient.pregnancy_status,
        'preferred_pharmacy': patient.preferred_pharmacy,
        'consent_terms': patient.consent_terms,
        'consent_telehealth': patient.consent_telehealth,
        'consent_reminders': patient.consent_reminders,
        'consent_marketing': patient.consent_marketing,
        'government_id_type': patient.government_id_type,
        'government_id_number': patient.government_id_number,
        'created_at': patient.created_at.isoformat() if patient.created_at else None,
    })


@patient_bp.route('/departments', methods=['GET'])
@token_required(roles=['patient'])
def departments(current_user):
    depts = Department.query.order_by(Department.name).all()
    return jsonify({'departments': [department_to_dict(d) for d in depts]})


@patient_bp.route('/summary', methods=['GET'])
@token_required(roles=['patient'])
def summary(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'Patient profile not found'}), 404

    now = datetime.utcnow()
    total = Appointment.query.filter_by(patient_id=patient.id).count()
    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_dt >= now,
        Appointment.status == 'booked'
    ).count()
    completed = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == 'completed'
    ).count()

    prescriptions = Appointment.query.join(Treatment).filter(
        Appointment.patient_id == patient.id,
        Treatment.prescription.isnot(None),
        Treatment.prescription != ''
    ).count()

    next_appt = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_dt >= now,
        Appointment.status == 'booked'
    ).order_by(Appointment.appointment_dt.asc()).first()

    return jsonify({
        'total_appointments': total,
        'upcoming_appointments': upcoming,
        'completed_appointments': completed,
        'active_prescriptions': prescriptions,
        'next_appointment': appointment_to_dict(next_appt) if next_appt else None
    })


def export_job_to_dict(job):
    return {
        'id': job.id,
        'status': job.status,
        'record_count': job.record_count or 0,
        'created_at': job.created_at.isoformat() if job.created_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
    }


@patient_bp.route('/notifications', methods=['GET'])
@token_required(roles=['patient'])
def notifications(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'Patient profile not found'}), 404

    now = datetime.utcnow()
    upcoming_limit = now + timedelta(days=7)
    upcoming_appts = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == 'booked',
        Appointment.appointment_dt >= now,
        Appointment.appointment_dt <= upcoming_limit
    ).order_by(Appointment.appointment_dt.asc()).limit(10).all()

    items = []
    for appt in upcoming_appts:
        doctor_name = appt.doctor.name if appt.doctor else 'your doctor'
        hours_left = (appt.appointment_dt - now).total_seconds() / 3600
        is_soon = hours_left <= 24
        items.append({
            'id': f'appointment-{appt.id}',
            'type': 'reminder' if is_soon else 'upcoming',
            'title': 'Appointment Reminder' if is_soon else 'Upcoming Appointment',
            'message': f'You have an appointment with {doctor_name} on {appt.appointment_dt.strftime("%b %d, %Y at %I:%M %p")}.',
            'time': appt.appointment_dt.isoformat()
        })

    recent_cutoff = now - timedelta(days=30)
    export_jobs = ExportJob.query.filter(
        ExportJob.patient_id == patient.id,
        ExportJob.completed_at.isnot(None),
        ExportJob.completed_at >= recent_cutoff
    ).order_by(ExportJob.completed_at.desc()).limit(10).all()

    for job in export_jobs:
        items.append({
            'id': f'export-{job.id}',
            'type': 'export',
            'title': 'Export Ready' if job.status == 'completed' else 'Export Failed',
            'message': (
                f'Your CSV export is ready ({job.record_count or 0} records).'
                if job.status == 'completed'
                else 'Your CSV export failed. Please try again.'
            ),
            'time': job.completed_at.isoformat() if job.completed_at else job.created_at.isoformat()
        })

    items.sort(key=lambda n: n['time'], reverse=True)

    return jsonify({'notifications': items})


@patient_bp.route('/doctors', methods=['GET'])
@token_required(roles=['patient'])
def doctors(current_user):
    q = (request.args.get('q') or '').strip()
    spec = (request.args.get('specialization') or '').strip()
    department_id = request.args.get('department_id', type=int)
    has_availability = (request.args.get('has_availability') or '').strip().lower() in ('1', 'true', 'yes')

    query = Doctor.query
    if q:
        pattern = f'%{q}%'
        query = query.filter(or_(Doctor.name.ilike(pattern), Doctor.specialization.ilike(pattern)))
    if spec:
        query = query.filter(Doctor.specialization.ilike(f'%{spec}%'))
    if department_id:
        query = query.filter(Doctor.department_id == department_id)

    today = date.today()
    if has_availability:
        subq = (
            db.session.query(DoctorAvailability.doctor_id)
            .filter(DoctorAvailability.available_date >= today)
            .distinct()
        )
        query = query.filter(Doctor.id.in_(subq))

    doctors = query.order_by(Doctor.name).all()

    doctor_ids = [d.id for d in doctors]
    has_slot_ids = set()
    if doctor_ids:
        rows = (
            db.session.query(DoctorAvailability.doctor_id)
            .filter(
                DoctorAvailability.doctor_id.in_(doctor_ids),
                DoctorAvailability.available_date >= today,
            )
            .distinct()
            .all()
        )
        has_slot_ids = {r[0] for r in rows}

    payload = []
    for d in doctors:
        row = doctor_to_dict(d)
        row['has_upcoming_availability'] = d.id in has_slot_ids
        payload.append(row)

    return jsonify({'doctors': payload})


@patient_bp.route('/availability', methods=['GET'])
@token_required(roles=['patient'])
def availability(current_user):
    doctor_id = request.args.get('doctor_id', type=int)
    if not doctor_id:
        return jsonify({'message': 'doctor_id required'}), 400
    avails = DoctorAvailability.query.filter_by(doctor_id=doctor_id).order_by(DoctorAvailability.available_date).all()
    return jsonify({'availability': [availability_to_dict(a) for a in avails]})


@patient_bp.route('/available-slots', methods=['GET'])
@token_required(roles=['patient'])
def available_slots(current_user):
    """
    Returns 30-min slots for a doctor on a given date, marking already booked times.
    Query params: doctor_id, date (YYYY-MM-DD)
    """
    doctor_id = request.args.get('doctor_id', type=int)
    date_str = (request.args.get('date') or '').strip()
    if not doctor_id or not date_str:
        return jsonify({'message': 'doctor_id and date are required (YYYY-MM-DD).'}), 400

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    slots = compute_slots_for_doctor_date(doctor_id, target_date)
    return jsonify({'slots': slots})


def _doctors_query_for_booking(specialization: str, department_id):
    query = Doctor.query
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
    if department_id:
        query = query.filter(Doctor.department_id == department_id)
    return query.order_by(Doctor.name)


@patient_bp.route('/booking/doctors-on-date', methods=['GET'])
@token_required(roles=['patient'])
def booking_doctors_on_date(current_user):
    """
    Doctors in a specialization with at least one free slot on the given date.
    Query: date (YYYY-MM-DD), specialization (optional), department_id (optional)
    """
    spec = (request.args.get('specialization') or '').strip()
    department_id = request.args.get('department_id', type=int)
    date_str = (request.args.get('date') or '').strip()
    if not date_str:
        return jsonify({'message': 'date is required (YYYY-MM-DD).'}), 400
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400
    if target_date < date.today():
        return jsonify({'message': 'Date must be today or later.'}), 400

    doctors = _doctors_query_for_booking(spec, department_id).all()
    payload = []
    for d in doctors:
        if doctor_has_free_slot(d.id, target_date):
            payload.append(doctor_to_dict(d))
    return jsonify({'doctors': payload})


@patient_bp.route('/booking/doctors-with-dates', methods=['GET'])
@token_required(roles=['patient'])
def booking_doctors_with_dates(current_user):
    """
    Doctors in a specialization with dates (from today) on which they have at least one free slot.
    Query: specialization (optional), department_id (optional), max_days (default 120, max 365)
    """
    spec = (request.args.get('specialization') or '').strip()
    department_id = request.args.get('department_id', type=int)
    max_days = request.args.get('max_days', type=int) or 120
    max_days = min(max(max_days, 1), 365)

    today = date.today()
    end_cutoff = today + timedelta(days=max_days)

    doctors = _doctors_query_for_booking(spec, department_id).all()
    out = []
    for d in doctors:
        date_rows = (
            db.session.query(DoctorAvailability.available_date)
            .filter(
                DoctorAvailability.doctor_id == d.id,
                DoctorAvailability.available_date >= today,
                DoctorAvailability.available_date <= end_cutoff,
            )
            .distinct()
            .order_by(DoctorAvailability.available_date.asc())
            .all()
        )
        available_dates = []
        for (dte,) in date_rows:
            if doctor_has_free_slot(d.id, dte):
                available_dates.append(dte.isoformat())
        if available_dates:
            out.append({
                'doctor': doctor_to_dict(d),
                'available_dates': available_dates,
            })
    return jsonify({'doctors': out})


@patient_bp.route('/appointments', methods=['GET', 'POST'])
@token_required(roles=['patient'])
def appointments(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'Patient profile not found'}), 404

    if request.method == 'POST':
        data = request.get_json() or {}
        doctor_id = data.get('doctor_id')
        appointment_dt = parse_dt(data.get('appointment_dt'))
        if not doctor_id or not appointment_dt:
            return jsonify({'message': 'doctor_id and appointment_dt are required (YYYY-MM-DD HH:MM).'}), 400

        # Prevent double booking for same doctor at same time
        conflict = Appointment.query.filter_by(doctor_id=doctor_id, appointment_dt=appointment_dt, status='booked').first()
        if conflict:
            return jsonify({'message': 'This time slot is already booked.'}), 409

        appt = Appointment(
            doctor_id=doctor_id,
            patient_id=patient.id,
            appointment_dt=appointment_dt,
            status='booked',
        )
        db.session.add(appt)
        db.session.flush()
        year_tag = appointment_dt.strftime('%y') if appointment_dt else None
        appt.appointment_uid = Appointment.format_appointment_uid(appt.id, year_tag)

        fu = FollowUp.query.filter(
            FollowUp.patient_id == patient.id,
            FollowUp.doctor_id == doctor_id,
            FollowUp.status.in_(['pending', 'missed'])
        ).order_by(FollowUp.due_date.asc()).first()
        if fu:
            fu.status = 'booked'
            fu.fulfilled_appointment_id = appt.id

        db.session.commit()
        return jsonify({'appointment': appointment_to_dict(appt)}), 201

    appts = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.appointment_dt.desc()).all()
    return jsonify({'appointments': [appointment_to_dict(a) for a in appts]})


@patient_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@token_required(roles=['patient'])
def update_appointment(current_user, appointment_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appt = Appointment.query.get_or_404(appointment_id)
    if appt.patient_id != patient.id:
        return jsonify({'message': 'Not allowed'}), 403

    data = request.get_json() or {}
    if 'status' in data:
        appt.status = data['status']

    if 'appointment_dt' in data:
        new_dt = parse_dt(data['appointment_dt'])
        if not new_dt:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD HH:MM.'}), 400
        conflict = Appointment.query.filter_by(doctor_id=appt.doctor_id, appointment_dt=new_dt, status='booked').first()
        if conflict and conflict.id != appt.id:
            return jsonify({'message': 'This time slot is already booked.'}), 409
        appt.appointment_dt = new_dt

    db.session.commit()
    return jsonify({'appointment': appointment_to_dict(appt)})


@patient_bp.route('/follow-ups', methods=['GET'])
@token_required(roles=['patient'])
def follow_ups_list(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'Patient profile not found'}), 404

    today = date.today()
    rows = FollowUp.query.filter(
        FollowUp.patient_id == patient.id,
        FollowUp.status.in_(['pending', 'missed'])
    ).order_by(FollowUp.due_date.asc()).all()

    changed = False
    for fu in rows:
        if fu.status == 'pending' and fu.due_date < today:
            fu.status = 'missed'
            changed = True
    if changed:
        db.session.commit()
        rows = FollowUp.query.filter(
            FollowUp.patient_id == patient.id,
            FollowUp.status.in_(['pending', 'missed'])
        ).order_by(FollowUp.due_date.asc()).all()

    return jsonify({'follow_ups': [follow_up_to_dict(fu, today) for fu in rows]})


@patient_bp.route('/treatments', methods=['GET'])
@token_required(roles=['patient'])
def treatments(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appts = Appointment.query.filter_by(patient_id=patient.id).all()
    payload = [appointment_to_dict(a) for a in appts if a.treatment]
    return jsonify({'treatments': payload})


@patient_bp.route('/prescriptions', methods=['GET'])
@token_required(roles=['patient'])
def prescriptions(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appts = Appointment.query.filter_by(patient_id=patient.id).all()
    payload = [
        appointment_to_dict(a)
        for a in appts
        if a.treatment and (a.treatment.prescription or '').strip()
    ]
    return jsonify({'prescriptions': payload})


@patient_bp.route('/exports', methods=['POST'])
@token_required(roles=['patient'])
def create_export(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'Patient profile not found'}), 404

    job = ExportJob(patient_id=patient.id, status='queued')
    db.session.add(job)
    db.session.commit()

    from ..jobs.tasks import export_csv_async
    export_csv_async.apply_async(args=[job.id])

    return jsonify({'export_job': export_job_to_dict(job)}), 202


@patient_bp.route('/exports', methods=['GET'])
@token_required(roles=['patient'])
def list_exports(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'Patient profile not found'}), 404

    jobs = ExportJob.query.filter_by(patient_id=patient.id).order_by(ExportJob.created_at.desc()).all()
    return jsonify({'exports': [export_job_to_dict(j) for j in jobs]})


@patient_bp.route('/exports/<int:job_id>', methods=['GET'])
@token_required(roles=['patient'])
def export_status(current_user, job_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'Patient profile not found'}), 404

    job = ExportJob.query.get_or_404(job_id)
    if job.patient_id != patient.id:
        return jsonify({'message': 'Not found'}), 404

    return jsonify({'export_job': export_job_to_dict(job)})


@patient_bp.route('/exports/<int:job_id>/download', methods=['GET'])
@token_required(roles=['patient'])
def download_export(current_user, job_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'Patient profile not found'}), 404

    job = ExportJob.query.get_or_404(job_id)
    if job.patient_id != patient.id:
        return jsonify({'message': 'Not found'}), 404
    if job.status != 'completed' or not job.file_path:
        return jsonify({'message': 'Export not ready'}), 409
    if not os.path.exists(job.file_path):
        return jsonify({'message': 'Export file missing'}), 404

    return send_file(
        job.file_path,
        as_attachment=True,
        download_name=os.path.basename(job.file_path)
    )


@patient_bp.route('/export', methods=['GET'])
@token_required(roles=['patient'])
def export_csv(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appts = Appointment.query.filter_by(patient_id=patient.id).all()
    rows = ['appointment_id,doctor,appointment_date,diagnosis,prescription,notes']
    for a in appts:
        diagnosis = (a.treatment.diagnosis or '') if a.treatment else ''
        prescription = (a.treatment.prescription or '') if a.treatment else ''
        notes = (a.treatment.notes or '') if a.treatment else ''
        rows.append(
            f'{a.id},"{a.doctor.name}","{a.appointment_dt}","{diagnosis}","{prescription}","{notes}"'
        )
    csv_data = '\n'.join(rows)
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=treatments.csv'}
    )
