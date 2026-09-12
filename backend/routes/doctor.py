from flask import Blueprint, request, jsonify, Response, send_file
from datetime import datetime, timedelta, date
import csv
import io

from ..models import db, Doctor, Appointment, Treatment, DoctorAvailability, Patient, FollowUp, User, MonthlyReport
from werkzeug.security import generate_password_hash, check_password_hash
from ..auth.routes import token_required
from .utils import appointment_to_dict, availability_to_dict, doctor_to_dict, patient_to_dict, parse_dt, monthly_report_to_dict

doctor_bp = Blueprint('doctor', __name__)
ALLOWED_APPOINTMENT_STATUSES = {'booked', 'completed', 'cancelled'}


def is_strong_password(password: str) -> bool:
    pwd = str(password or '')
    return (
        len(pwd) >= 8
        and any(c.islower() for c in pwd)
        and any(c.isupper() for c in pwd)
        and any(c.isdigit() for c in pwd)
        and any(not c.isalnum() for c in pwd)
    )


def _current_doctor(current_user):
    return Doctor.query.filter_by(user_id=current_user.id).first()


def _bad_request(message, details=None):
    payload = {'message': message}
    if details:
        payload['details'] = details
    return jsonify(payload), 400


def _auto_cancel_overdue_appointments(doctor_id, now=None):
    now = now or datetime.utcnow()
    overdue = Appointment.query.filter_by(doctor_id=doctor_id, status='booked') \
        .filter(Appointment.appointment_dt < now).all()
    if not overdue:
        return 0
    for appt in overdue:
        appt.status = 'cancelled'
    db.session.commit()
    return len(overdue)


def _apply_follow_up_payload(appt, data):
    """Create/update/delete FollowUp from PATCH body (follow_up_days or follow_up_date)."""
    if 'follow_up_days' not in data and 'follow_up_date' not in data:
        return None

    raw_days = data.get('follow_up_days')
    fu_date_raw = data.get('follow_up_date')

    if fu_date_raw is not None and str(fu_date_raw).strip() != '':
        try:
            due = datetime.strptime(str(fu_date_raw).strip()[:10], '%Y-%m-%d').date()
        except ValueError:
            return 'follow_up_date must be YYYY-MM-DD.'

        existing = FollowUp.query.filter_by(source_appointment_id=appt.id).first()
        if existing and existing.status == 'booked':
            return None
        if not existing:
            db.session.add(FollowUp(
                source_appointment_id=appt.id,
                patient_id=appt.patient_id,
                doctor_id=appt.doctor_id,
                due_date=due,
                days_interval=None,
                status='pending',
            ))
        else:
            existing.due_date = due
            existing.days_interval = None
            if existing.status == 'missed':
                existing.status = 'pending'
        return None

    if raw_days is not None and str(raw_days).strip() != '':
        try:
            n_days = int(raw_days)
        except (TypeError, ValueError):
            return 'follow_up_days must be a non-negative integer.'
        if n_days < 0:
            return 'follow_up_days must be non-negative.'
        base = appt.appointment_dt.date() if appt.appointment_dt else date.today()
        due = base + timedelta(days=n_days)

        existing = FollowUp.query.filter_by(source_appointment_id=appt.id).first()
        if existing and existing.status == 'booked':
            return None
        if not existing:
            db.session.add(FollowUp(
                source_appointment_id=appt.id,
                patient_id=appt.patient_id,
                doctor_id=appt.doctor_id,
                due_date=due,
                days_interval=n_days,
                status='pending',
            ))
        else:
            existing.due_date = due
            existing.days_interval = n_days
            if existing.status == 'missed':
                existing.status = 'pending'
        return None

    existing = FollowUp.query.filter_by(source_appointment_id=appt.id).first()
    if existing and existing.status != 'booked':
        db.session.delete(existing)
    return None


@doctor_bp.route('/profile', methods=['GET', 'PUT'])
@token_required(roles=['doctor'])
def profile(current_user):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404

    if request.method == 'PUT':
        data = request.get_json() or {}
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
        for field in ('name', 'specialization', 'qualification', 'experience_years', 'bio', 'department_id'):
            if field in data:
                setattr(doctor, field, data[field])
        if 'email' in data and doctor.user:
            doctor.user.email = (data['email'] or '').strip().lower()
        db.session.commit()

    return jsonify({'doctor': doctor_to_dict(doctor)})


@doctor_bp.route('/summary', methods=['GET'])
@token_required(roles=['doctor'])
def summary(current_user):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404

    now = datetime.utcnow()
    _auto_cancel_overdue_appointments(doctor.id, now=now)
    today = now.date()
    today_start = datetime(today.year, today.month, today.day)
    today_end = today_start + timedelta(days=1)

    base = Appointment.query.filter_by(doctor_id=doctor.id)

    today_count = base.filter(
        Appointment.appointment_dt >= today_start,
        Appointment.appointment_dt < today_end
    ).count()

    upcoming_count = base.filter(
        Appointment.appointment_dt >= now,
        Appointment.status == 'booked'
    ).count()

    completed_count = base.filter(Appointment.status == 'completed').count()

    patient_ids = {
        a.patient_id for a in base.with_entities(Appointment.patient_id).distinct().all()
        if a.patient_id is not None
    }

    next_appt = base.filter(
        Appointment.appointment_dt >= now,
        Appointment.status == 'booked'
    ).order_by(Appointment.appointment_dt.asc()).first()

    return jsonify({
        'today_appointments': today_count,
        'upcoming_appointments': upcoming_count,
        'completed_appointments': completed_count,
        'total_patients': len(patient_ids),
        'next_appointment': appointment_to_dict(next_appt) if next_appt else None
    })


@doctor_bp.route('/appointments', methods=['GET'])
@token_required(roles=['doctor'])
def doctor_appointments(current_user):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404
    _auto_cancel_overdue_appointments(doctor.id)
    status = (request.args.get('status') or '').strip().lower()
    from_raw = (request.args.get('from') or '').strip()
    to_raw = (request.args.get('to') or '').strip()
    from_dt = parse_dt(from_raw)
    to_dt = parse_dt(to_raw)
    if from_raw and not from_dt:
        return _bad_request('Invalid from datetime. Use YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM.')
    if to_raw and not to_dt:
        return _bad_request('Invalid to datetime. Use YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM.')
    if status and status not in ALLOWED_APPOINTMENT_STATUSES:
        return _bad_request(f'Invalid status. Allowed: {", ".join(sorted(ALLOWED_APPOINTMENT_STATUSES))}.')
    query = Appointment.query.filter_by(doctor_id=doctor.id)
    if status:
        query = query.filter_by(status=status)
    if from_dt:
        query = query.filter(Appointment.appointment_dt >= from_dt)
    if to_dt:
        query = query.filter(Appointment.appointment_dt <= to_dt)
    appts = query.order_by(Appointment.appointment_dt.desc()).all()
    return jsonify({'appointments': [appointment_to_dict(a) for a in appts]})


@doctor_bp.route('/reports', methods=['GET'])
@token_required(roles=['doctor'])
def list_doctor_reports(current_user):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404
    
    reports = MonthlyReport.query.filter_by(doctor_id=doctor.id).order_by(MonthlyReport.generated_at.desc()).all()
    return jsonify({'reports': [monthly_report_to_dict(r) for r in reports]})


@doctor_bp.route('/reports/<int:report_id>/download', methods=['GET'])
@token_required(roles=['doctor'])
def download_doctor_report(current_user, report_id):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404
    
    report = MonthlyReport.query.get_or_404(report_id)
    if report.doctor_id != doctor.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    return send_file(report.file_path, mimetype='text/html', as_attachment=True, download_name=f'Report_{report.report_month.replace(" ", "_")}.html')


@doctor_bp.route('/reports/instant', methods=['POST'])
@token_required(roles=['doctor'])
def trigger_instant_report(current_user):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404
    
    from ..jobs.tasks import generate_instant_doctor_report
    result = generate_instant_doctor_report(doctor.id)
    return jsonify(result)


@doctor_bp.route('/reports/legacy-monthly', methods=['GET'])
@token_required(roles=['doctor'])
def doctor_monthly_report(current_user):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    fmt = (request.args.get('format') or 'html').strip().lower()
    download = request.args.get('download', type=int) == 1
    now = datetime.utcnow()
    if not year or not month:
        # default to previous month
        first_of_this_month = datetime(now.year, now.month, 1)
        prev_month_end = first_of_this_month - timedelta(days=1)
        year = prev_month_end.year
        month = prev_month_end.month
    if month < 1 or month > 12:
        return _bad_request('month must be between 1 and 12.')
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end = datetime(year, month + 1, 1) - timedelta(seconds=1)

    appts = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_dt >= start,
        Appointment.appointment_dt <= end,
    ).order_by(Appointment.appointment_dt.asc()).all()

    def appt_uid(appt):
        if appt.appointment_uid:
            return appt.appointment_uid
        return Appointment.format_appointment_uid(appt.id, str(year)[-2:])

    rows = []
    for appt in appts:
        patient = Patient.query.get(appt.patient_id) if appt.patient_id else None
        treatment = appt.treatment
        rows.append({
            'appointment_uid': appt_uid(appt),
            'date': appt.appointment_dt.strftime('%b %d, %Y') if appt.appointment_dt else '',
            'time': appt.appointment_dt.strftime('%I:%M %p') if appt.appointment_dt else '',
            'patient': patient.full_name if patient else '',
            'status': appt.status or '',
            'diagnosis': treatment.diagnosis if treatment else '',
            'prescription': treatment.prescription if treatment else '',
            'notes': treatment.notes if treatment else '',
        })

    month_label = start.strftime('%B %Y')
    html_rows = ''.join([
        f'''
        <tr>
          <td>{r["appointment_uid"]}</td>
          <td>{r["date"]}</td>
          <td>{r["time"]}</td>
          <td>{r["patient"]}</td>
          <td>{r["status"].title()}</td>
          <td>{r["diagnosis"]}</td>
          <td>{r["prescription"]}</td>
          <td>{r["notes"]}</td>
        </tr>
        ''' for r in rows
    ]) or '<tr><td colspan="8" style="padding:12px;color:#64748b">No appointments recorded.</td></tr>'

    html = f"""
    <html>
      <body style="font-family:Arial,Helvetica,sans-serif;color:#0f172a;background:#f8fafc;padding:20px">
        <div style="max-width:900px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:20px">
          <h2 style="margin:0 0 6px 0">Monthly Activity Report</h2>
          <div style="color:#64748b;margin-bottom:16px">{month_label}</div>
          <div style="margin-bottom:12px">
            <strong>Doctor:</strong> {doctor.name}<br/>
            <strong>Specialization:</strong> {doctor.specialization}<br/>
            <strong>Appointments:</strong> {len(rows)}
          </div>
          <table style="width:100%;border-collapse:collapse;font-size:12px">
            <thead>
              <tr>
                <th style="text-align:left;border-bottom:1px solid #e2e8f0;padding:8px">Appt ID</th>
                <th style="text-align:left;border-bottom:1px solid #e2e8f0;padding:8px">Date</th>
                <th style="text-align:left;border-bottom:1px solid #e2e8f0;padding:8px">Time</th>
                <th style="text-align:left;border-bottom:1px solid #e2e8f0;padding:8px">Patient</th>
                <th style="text-align:left;border-bottom:1px solid #e2e8f0;padding:8px">Status</th>
                <th style="text-align:left;border-bottom:1px solid #e2e8f0;padding:8px">Diagnosis</th>
                <th style="text-align:left;border-bottom:1px solid #e2e8f0;padding:8px">Prescription</th>
                <th style="text-align:left;border-bottom:1px solid #e2e8f0;padding:8px">Notes</th>
              </tr>
            </thead>
            <tbody>
              {html_rows}
            </tbody>
          </table>
        </div>
      </body>
    </html>
    """

    if fmt != 'html':
        return _bad_request('Only html format is supported right now.')
    response = Response(html, mimetype='text/html')
    if download:
        filename = f'doctor-report-{year}-{str(month).zfill(2)}.html'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@doctor_bp.route('/appointments/<int:appointment_id>', methods=['PATCH'])
@token_required(roles=['doctor'])
def update_appointment(current_user, appointment_id):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404
    appt = Appointment.query.get_or_404(appointment_id)
    if appt.doctor_id != doctor.id:
        return jsonify({'message': 'Not allowed'}), 403

    data = request.get_json() or {}
    if 'status' in data:
        status = (data['status'] or '').strip().lower()
        if status not in ALLOWED_APPOINTMENT_STATUSES:
            return _bad_request(f'Invalid status. Allowed: {", ".join(sorted(ALLOWED_APPOINTMENT_STATUSES))}.')
        appt.status = status

    if 'appointment_dt' in data:
        appointment_dt = parse_dt((data.get('appointment_dt') or '').strip())
        if not appointment_dt:
            return _bad_request('Invalid appointment_dt. Use YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM.')
        conflict = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.id != appt.id,
            Appointment.appointment_dt == appointment_dt,
            Appointment.status == 'booked'
        ).first()
        if conflict:
            return _bad_request('Doctor already has a booked appointment at this time.')
        appt.appointment_dt = appointment_dt

    if any(k in data for k in ('diagnosis', 'prescription', 'notes')):
        treatment = Treatment.query.filter_by(appointment_id=appt.id).first()
        if not treatment:
            treatment = Treatment(appointment_id=appt.id)
            db.session.add(treatment)
        if 'diagnosis' in data:
            treatment.diagnosis = data['diagnosis']
        if 'prescription' in data:
            treatment.prescription = data['prescription']
        if 'notes' in data:
            treatment.notes = data['notes']

    err = _apply_follow_up_payload(appt, data)
    if err:
        return _bad_request(err)

    db.session.commit()
    return jsonify({'appointment': appointment_to_dict(appt)})


@doctor_bp.route('/availability', methods=['GET', 'POST'])
@token_required(roles=['doctor'])
def availability(current_user):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404

    if request.method == 'POST':
        data = request.get_json() or {}
        slots = data.get('slots') or []
        replace_dates = data.get('replace_dates') or []
        if isinstance(slots, dict):
            slots = [slots]
        if not isinstance(slots, list):
            return _bad_request('slots must be a list or object.')
        if replace_dates and not isinstance(replace_dates, list):
            return _bad_request('replace_dates must be a list (YYYY-MM-DD).')
        # Replace availability for the provided dates (avoid "toggling off" being ineffective).
        # Without this, old entries would remain and patient slot availability would not shrink.
        slot_dates = set()
        for d in replace_dates:
            try:
                slot_dates.add(datetime.strptime(str(d), '%Y-%m-%d').date())
            except Exception:
                return _bad_request('replace_dates entries must be YYYY-MM-DD.')
        for s in slots:
            if not s or not s.get('available_date'):
                continue
            try:
                slot_dates.add(datetime.strptime(s['available_date'], '%Y-%m-%d').date())
            except Exception:
                continue
        if slot_dates:
            DoctorAvailability.query.filter(
                DoctorAvailability.doctor_id == doctor.id,
                DoctorAvailability.available_date.in_(slot_dates),
            ).delete(synchronize_session=False)
            db.session.commit()

        created = []
        rejected = []
        for s in slots:
            if not s.get('available_date') or not s.get('start_time') or not s.get('end_time'):
                rejected.append({'slot': s, 'reason': 'available_date/start_time/end_time required'})
                continue
            try:
                available_date = datetime.strptime(s['available_date'], '%Y-%m-%d').date()
            except Exception:
                rejected.append({'slot': s, 'reason': 'available_date must be YYYY-MM-DD'})
                continue
            if s['start_time'] >= s['end_time']:
                rejected.append({'slot': s, 'reason': 'start_time must be before end_time'})
                continue
            avail = DoctorAvailability(
                doctor_id=doctor.id,
                available_date=available_date,
                start_time=s['start_time'],
                end_time=s['end_time'],
                max_slots=s.get('max_slots') or 10
            )
            db.session.add(avail)
            created.append(avail)
        db.session.commit()
        return jsonify({
            'availability': [availability_to_dict(a) for a in created],
            'rejected': rejected
        })

    avails = DoctorAvailability.query.filter_by(doctor_id=doctor.id).order_by(DoctorAvailability.available_date).all()
    return jsonify({'availability': [availability_to_dict(a) for a in avails]})


@doctor_bp.route('/patients', methods=['GET'])
@token_required(roles=['doctor'])
def doctor_patients(current_user):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404
    patient_ids = {a.patient_id for a in Appointment.query.filter_by(doctor_id=doctor.id).all()}
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all() if patient_ids else []
    return jsonify({'patients': [patient_to_dict(p) for p in patients]})


@doctor_bp.route('/patients', methods=['POST'])
@token_required(roles=['doctor'])
def doctor_create_patient(current_user):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404
    data = request.get_json() or {}
    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    phone = (data.get('phone') or '').strip()
    birth_year = str(data.get('birth_year') or '').strip()
    password = (data.get('password') or '').strip()
    gender = (data.get('gender') or '').strip() or 'Other'

    if not first_name:
        return _bad_request('first_name is required.')
    if not last_name:
        return _bad_request('last_name is required.')
    if not phone:
        return _bad_request('phone is required.')
    if not email:
        return _bad_request('email is required.')
    if not birth_year or not birth_year.isdigit() or len(birth_year) != 4:
        return _bad_request('birth_year must be a 4-digit year.')
    if not password:
        return _bad_request('password is required.')

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'An account with this email already exists.'}), 409
    if Patient.query.filter_by(phone=phone).first():
        return jsonify({'message': 'An account with this phone number already exists.'}), 409

    try:
        dob = datetime.strptime(f'{birth_year}-01-01', '%Y-%m-%d').date()
    except ValueError:
        return _bad_request('Invalid birth_year.')

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role='patient',
        is_active=True
    )
    db.session.add(user)
    db.session.flush()

    patient = Patient(
        user_id=user.id,
        patient_uid=Patient.generate_patient_uid(),
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        dob=dob,
        gender=gender
    )
    db.session.add(patient)
    db.session.commit()

    return jsonify({'patient': patient_to_dict(patient)}), 201


@doctor_bp.route('/treatments', methods=['GET'])
@token_required(roles=['doctor'])
def doctor_treatments(current_user):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404

    patient_id = request.args.get('patient_id', type=int)
    from_raw = (request.args.get('from') or '').strip()
    to_raw = (request.args.get('to') or '').strip()
    from_dt = parse_dt(from_raw)
    to_dt = parse_dt(to_raw)
    if from_raw and not from_dt:
        return _bad_request('Invalid from datetime. Use YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM.')
    if to_raw and not to_dt:
        return _bad_request('Invalid to datetime. Use YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM.')

    query = Appointment.query.filter_by(doctor_id=doctor.id).join(Treatment, isouter=True)
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    if from_dt:
        query = query.filter(Appointment.appointment_dt >= from_dt)
    if to_dt:
        query = query.filter(Appointment.appointment_dt <= to_dt)

    appts = query.order_by(Appointment.appointment_dt.desc()).all()
    payload = [appointment_to_dict(a) for a in appts if a.treatment]
    return jsonify({'treatments': payload})


@doctor_bp.route('/appointments', methods=['POST'])
@token_required(roles=['doctor'])
def create_appointment(current_user):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404

    data = request.get_json() or {}
    patient_id = data.get('patient_id')
    appointment_dt = parse_dt((data.get('appointment_dt') or '').strip())
    status = (data.get('status') or 'booked').strip().lower()
    if not patient_id:
        return _bad_request('patient_id is required.')
    if not appointment_dt:
        return _bad_request('appointment_dt is required and must be YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM.')
    if status not in ALLOWED_APPOINTMENT_STATUSES:
        return _bad_request(f'Invalid status. Allowed: {", ".join(sorted(ALLOWED_APPOINTMENT_STATUSES))}.')
    patient = Patient.query.get(patient_id)
    if not patient:
        return _bad_request('Patient not found.')

    conflict = Appointment.query.filter_by(
        doctor_id=doctor.id,
        appointment_dt=appointment_dt,
        status='booked'
    ).first()
    if conflict:
        return _bad_request('Doctor already has a booked appointment at this time.')

    appt = Appointment(
        doctor_id=doctor.id,
        patient_id=patient_id,
        appointment_dt=appointment_dt,
        status=status,
    )
    db.session.add(appt)
    db.session.flush()
    year_tag = appointment_dt.strftime('%y') if appointment_dt else None
    appt.appointment_uid = Appointment.format_appointment_uid(appt.id, year_tag)
    db.session.commit()
    return jsonify({'appointment': appointment_to_dict(appt)}), 201


@doctor_bp.route('/notifications', methods=['GET'])
@token_required(roles=['doctor'])
def doctor_notifications(current_user):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404

    limit = request.args.get('limit', type=int) or 20
    limit = max(1, min(limit, 100))

    now = datetime.utcnow()
    upcoming = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status == 'booked',
        Appointment.appointment_dt >= now
    ).order_by(Appointment.appointment_dt.asc()).limit(limit).all()

    recent_cancelled = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status == 'cancelled'
    ).order_by(Appointment.appointment_dt.desc()).limit(max(3, limit // 3)).all()

    notifications = []
    for appt in upcoming:
        patient_name = appt.patient.full_name if appt.patient else 'Patient'
        notifications.append({
            'id': f'upcoming-{appt.id}',
            'type': 'appointment',
            'title': 'Upcoming Appointment',
            'message': f'{patient_name} at {appt.appointment_dt.strftime("%b %d, %Y %I:%M %p")}',
            'created_at': appt.appointment_dt.isoformat(timespec='minutes')
        })
    for appt in recent_cancelled:
        patient_name = appt.patient.full_name if appt.patient else 'Patient'
        notifications.append({
            'id': f'cancelled-{appt.id}',
            'type': 'cancelled',
            'title': 'Appointment Cancelled',
            'message': f'{patient_name} appointment marked cancelled',
            'created_at': appt.appointment_dt.isoformat(timespec='minutes')
        })

    notifications.sort(key=lambda n: n['created_at'], reverse=True)
    return jsonify({'notifications': notifications[:limit]})


@doctor_bp.route('/export', methods=['GET'])
@token_required(roles=['doctor'])
def doctor_export(current_user):
    doctor = _current_doctor(current_user)
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404

    from_raw = (request.args.get('from') or '').strip()
    to_raw = (request.args.get('to') or '').strip()
    from_dt = parse_dt(from_raw)
    to_dt = parse_dt(to_raw)
    if from_raw and not from_dt:
        return _bad_request('Invalid from datetime. Use YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM.')
    if to_raw and not to_dt:
        return _bad_request('Invalid to datetime. Use YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM.')

    query = Appointment.query.filter_by(doctor_id=doctor.id)
    if from_dt:
        query = query.filter(Appointment.appointment_dt >= from_dt)
    if to_dt:
        query = query.filter(Appointment.appointment_dt <= to_dt)
    appts = query.order_by(Appointment.appointment_dt.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'appointment_id', 'appointment_datetime', 'status', 'patient_name',
        'patient_id', 'diagnosis', 'prescription', 'notes'
    ])
    for appt in appts:
        writer.writerow([
            appt.id,
            appt.appointment_dt.isoformat(timespec='minutes'),
            appt.status,
            appt.patient.full_name if appt.patient else '',
            appt.patient_id,
            appt.treatment.diagnosis if appt.treatment else '',
            appt.treatment.prescription if appt.treatment else '',
            appt.treatment.notes if appt.treatment else '',
        ])

    csv_content = output.getvalue()
    output.close()
    filename = f'doctor_activity_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )
