from flask import Blueprint, request, jsonify, send_file
from werkzeug.security import generate_password_hash
from ..jobs.tasks import _send_email
from datetime import datetime, date
from ..models import db, User, Doctor, Patient, Appointment, Department, DoctorAvailability, MonthlyReport
from ..auth.routes import token_required
from .utils import doctor_to_dict, patient_to_dict, appointment_to_dict, department_to_dict, parse_dt, availability_to_dict, monthly_report_to_dict
from .patient import compute_slots_for_doctor_date, doctor_has_free_slot

admin_bp = Blueprint('admin', __name__)


def _clean_optional(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _parse_date(value, field_name):
    cleaned = _clean_optional(value)
    if cleaned is None:
        return None
    try:
        return datetime.strptime(cleaned, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(f'Invalid {field_name}. Use YYYY-MM-DD format.')


def _department_patient_count(department_id):
    return len({
        a.patient_id
        for a in Appointment.query.join(Doctor, Appointment.doctor_id == Doctor.id).filter(
            Doctor.department_id == department_id,
            Appointment.patient_id.isnot(None)
        ).all()
    })


def _parse_optional_float(value, field_name):
    cleaned = _clean_optional(value)
    if cleaned is None:
        return None
    try:
        return float(cleaned)
    except (TypeError, ValueError):
        raise ValueError(f'Invalid {field_name}. Must be a number.')


@admin_bp.route('/summary', methods=['GET'])
@token_required(roles=['admin'])
def summary(current_user):
    return jsonify({
        "doctors": Doctor.query.count(),
        "patients": Patient.query.count(),
        "appointments": Appointment.query.count()
    })


@admin_bp.route('/departments', methods=['GET', 'POST'])
@token_required(roles=['admin'])
def departments(current_user):
    if request.method == 'POST':
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'message': 'Department name required'}), 400
        if Department.query.filter_by(name=name).first():
            return jsonify({'message': 'Department already exists'}), 409
        dept = Department(
            department_uid=Department.generate_department_uid(),
            name=name,
            description=data.get('description')
        )
        db.session.add(dept)
        db.session.commit()
        return jsonify({'department': department_to_dict(dept)}), 201

    depts = Department.query.order_by(Department.name).all()
    payload = []
    for d in depts:
        dd = department_to_dict(d)
        dd['patient_count'] = _department_patient_count(d.id)
        payload.append(dd)
    return jsonify({'departments': payload})


@admin_bp.route('/departments/<int:department_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required(roles=['admin'])
def department_detail(current_user, department_id):
    dept = Department.query.get_or_404(department_id)

    if request.method == 'GET':
        doctors = Doctor.query.filter_by(department_id=dept.id).order_by(Doctor.name).all()
        dept_payload = department_to_dict(dept)
        dept_payload['patient_count'] = _department_patient_count(dept.id)
        return jsonify({
            'department': dept_payload,
            'doctors': [doctor_to_dict(d) for d in doctors]
        })

    if request.method == 'DELETE':
        has_doctors = Doctor.query.filter_by(department_id=dept.id).first() is not None
        if has_doctors:
            return jsonify({'message': 'Cannot delete department with assigned doctors.'}), 409
        db.session.delete(dept)
        db.session.commit()
        return jsonify({'message': 'Department deleted'}), 200

    data = request.get_json() or {}
    if 'name' in data:
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'message': 'Department name required'}), 400
        existing = Department.query.filter(Department.name == name, Department.id != dept.id).first()
        if existing:
            return jsonify({'message': 'Department name already exists'}), 409
        dept.name = name
    if 'description' in data:
        dept.description = _clean_optional(data.get('description'))

    db.session.commit()
    return jsonify({'department': department_to_dict(dept)})


@admin_bp.route('/doctors', methods=['GET', 'POST'])
@token_required(roles=['admin'])
def doctors(current_user):
    if request.method == 'POST':
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip().lower()
        specialization = (data.get('specialization') or '').strip()
        department = Department.query.filter_by(name=specialization).first() if specialization else None
        password = data.get('password') or 'Doctor@1234'
        if not name or not email or not specialization:
            return jsonify({'message': 'Name, email and specialization are required.'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already exists.'}), 409

        user = User(email=email, password_hash=generate_password_hash(password), role='doctor', is_active=True)
        db.session.add(user)
        db.session.flush()

        try:
            appointment_fee = _parse_optional_float(data.get('appointment_fee'), 'appointment fee')
        except ValueError as ex:
            return jsonify({'message': str(ex)}), 400

        doc = Doctor(
            doctor_uid=Doctor.generate_doctor_uid(),
            user_id=user.id,
            name=name,
            gender=_clean_optional(data.get('gender')),
            specialization=specialization,
            department_id=department.id if department else None,
            qualification=data.get('qualification'),
            sub_specialties=_clean_optional(data.get('sub_specialties')),
            languages_spoken=_clean_optional(data.get('languages_spoken')),
            certifications=_clean_optional(data.get('certifications')),
            awards=_clean_optional(data.get('awards')),
            past_experience=_clean_optional(data.get('past_experience')),
            appointment_fee=appointment_fee,
            experience_years=data.get('experience_years') or 0,
            bio=data.get('bio')
        )
        db.session.add(doc)
        db.session.commit()
        credentials_sent = False
        if email:
            subject = 'Your Doctor Account Credentials'
            body = (
                f'Hello Dr. {name},\n\n'
                f'Your doctor account has been created.\n'
                f'Login email: {email}\n'
                f'Temporary password: {password}\n\n'
                f'Please log in and change your password after first login.'
            )
            credentials_sent = _send_email(email, subject, body)
        return jsonify({
            'doctor': doctor_to_dict(doc),
            'temp_password': password,
            'credentials_email_sent': credentials_sent
        }), 201

    q = (request.args.get('q') or '').strip().lower()
    spec = (request.args.get('specialization') or '').strip().lower()
    dept_id = (request.args.get('department_id') or '').strip()
    date_str = (request.args.get('date') or '').strip()
    time_str = (request.args.get('time') or '').strip()
    query = Doctor.query
    if q:
        query = query.filter(Doctor.name.ilike(f'%{q}%'))
    if spec:
        query = query.filter(Doctor.specialization.ilike(f'%{spec}%'))
    if dept_id:
        try:
            query = query.filter(Doctor.department_id == int(dept_id))
        except ValueError:
            pass
    doctors = query.order_by(Doctor.name).all()

    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            filtered_doctors = []
            for d in doctors:
                slots = compute_slots_for_doctor_date(d.id, target_date)
                if time_str:
                    if any(s['time'] == time_str and s['available'] for s in slots):
                        filtered_doctors.append(d)
                else:
                    if any(s['available'] for s in slots):
                        filtered_doctors.append(d)
            doctors = filtered_doctors
        except ValueError:
            pass

    payload = []
    for d in doctors:
        dd = doctor_to_dict(d)
        dd['is_blacklisted'] = d.user.is_blacklisted if d.user else False
        payload.append(dd)
    return jsonify({'doctors': payload})


@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT', 'DELETE'])
@token_required(roles=['admin'])
def doctor_detail(current_user, doctor_id):
    doc = Doctor.query.get_or_404(doctor_id)
    if request.method == 'DELETE':
        if doc.user:
            doc.user.is_blacklisted = True
            db.session.commit()
        return jsonify({'message': 'Doctor blacklisted'}), 200

    data = request.get_json() or {}

    # Email uniqueness check
    if 'email' in data and doc.user:
        new_email = data['email'].strip().lower()
        if new_email and new_email != doc.user.email:
            if User.query.filter_by(email=new_email).filter(User.id != doc.user_id).first():
                return jsonify({'message': 'Email already exists for another user.'}), 409
            doc.user.email = new_email

    # Password update
    if 'password' in data and data['password'] and doc.user:
        pass_val = data['password'].strip()
        if len(pass_val) >= 6:
            doc.user.password_hash = generate_password_hash(pass_val)

    if 'name' in data:
        doc.name = data.get('name', doc.name)
    if 'specialization' in data:
        specialization = (data.get('specialization') or '').strip()
        doc.specialization = specialization
        department = Department.query.filter_by(name=specialization).first() if specialization else None
        doc.department_id = department.id if department else None
    if 'gender' in data:
        doc.gender = _clean_optional(data.get('gender'))
    if 'qualification' in data:
        doc.qualification = data.get('qualification')
    if 'sub_specialties' in data:
        doc.sub_specialties = _clean_optional(data.get('sub_specialties'))
    if 'languages_spoken' in data:
        doc.languages_spoken = _clean_optional(data.get('languages_spoken'))
    if 'certifications' in data:
        doc.certifications = _clean_optional(data.get('certifications'))
    if 'awards' in data:
        doc.awards = _clean_optional(data.get('awards'))
    if 'past_experience' in data:
        doc.past_experience = _clean_optional(data.get('past_experience'))
    if 'appointment_fee' in data:
        try:
            doc.appointment_fee = _parse_optional_float(data.get('appointment_fee'), 'appointment fee')
        except ValueError as ex:
            return jsonify({'message': str(ex)}), 400
    if 'experience_years' in data:
        doc.experience_years = data.get('experience_years') or 0
    if 'bio' in data:
        doc.bio = data.get('bio')

    db.session.commit()
    return jsonify({'doctor': doctor_to_dict(doc)})


@admin_bp.route('/doctors/<int:doctor_id>/blacklist', methods=['PATCH'])
@token_required(roles=['admin'])
def toggle_doctor_blacklist(current_user, doctor_id):
    doc = Doctor.query.get_or_404(doctor_id)
    if doc.user:
        data = request.get_json() or {}
        target_status = data.get('blacklist', not doc.user.is_blacklisted)
        doc.user.is_blacklisted = target_status
        db.session.commit()
        return jsonify({'message': 'Doctor blacklisted' if target_status else 'Doctor activated'})
    return jsonify({'message': 'No user account attached'}), 400

@admin_bp.route('/doctors/<int:doctor_id>/availability', methods=['GET', 'POST'])
@token_required(roles=['admin'])
def doctor_availability(current_user, doctor_id):
    doc = Doctor.query.get_or_404(doctor_id)
    if request.method == 'POST':
        data = request.get_json() or {}
        if data.get('slots') is not None or data.get('replace_dates') is not None:
            slots = data.get('slots') or []
            replace_dates = data.get('replace_dates') or []
            if isinstance(slots, dict):
                slots = [slots]
            if not isinstance(slots, list):
                return jsonify({'message': 'slots must be a list or object.'}), 400
            if replace_dates and not isinstance(replace_dates, list):
                return jsonify({'message': 'replace_dates must be a list (YYYY-MM-DD).'}), 400

            slot_dates = set()
            for d in replace_dates:
                try:
                    slot_dates.add(datetime.strptime(str(d), '%Y-%m-%d').date())
                except Exception:
                    return jsonify({'message': 'replace_dates entries must be YYYY-MM-DD.'}), 400
            for s in slots:
                if not s or not s.get('available_date'):
                    continue
                try:
                    slot_dates.add(datetime.strptime(s['available_date'], '%Y-%m-%d').date())
                except Exception:
                    continue
            if slot_dates:
                DoctorAvailability.query.filter(
                    DoctorAvailability.doctor_id == doc.id,
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
                    doctor_id=doc.id,
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

        try:
            available_date = _parse_date(data.get('available_date'), 'available_date')
        except ValueError as ex:
            return jsonify({'message': str(ex)}), 400
        start_time = (data.get('start_time') or '').strip()
        end_time = (data.get('end_time') or '').strip()
        max_slots = data.get('max_slots') or 10
        if not available_date:
            return jsonify({'message': 'available_date is required.'}), 400
        if not start_time or not end_time:
            return jsonify({'message': 'start_time and end_time are required.'}), 400
        if start_time >= end_time:
            return jsonify({'message': 'start_time must be before end_time.'}), 400
        avail = DoctorAvailability(
            doctor_id=doc.id,
            available_date=available_date,
            start_time=start_time,
            end_time=end_time,
            max_slots=max_slots
        )
        db.session.add(avail)
        db.session.commit()
        return jsonify({'availability': {
            'id': avail.id,
            'available_date': avail.available_date.isoformat(),
            'start_time': avail.start_time,
            'end_time': avail.end_time,
            'max_slots': avail.max_slots,
        }}), 201

    avails = DoctorAvailability.query.filter_by(doctor_id=doc.id).order_by(DoctorAvailability.available_date).all()
    return jsonify({'availability': [
        {
            'id': a.id,
            'available_date': a.available_date.isoformat(),
            'start_time': a.start_time,
            'end_time': a.end_time,
            'max_slots': a.max_slots,
        } for a in avails
    ]})


@admin_bp.route('/doctors/<int:doctor_id>/availability/<int:avail_id>', methods=['PUT', 'DELETE'])
@token_required(roles=['admin'])
def doctor_availability_detail(current_user, doctor_id, avail_id):
    doc = Doctor.query.get_or_404(doctor_id)
    avail = DoctorAvailability.query.get_or_404(avail_id)
    if avail.doctor_id != doc.id:
        return jsonify({'message': 'Not allowed'}), 403
    if request.method == 'DELETE':
        db.session.delete(avail)
        db.session.commit()
        return jsonify({'message': 'Availability deleted'})
    data = request.get_json() or {}
    if 'available_date' in data:
        try:
            avail.available_date = _parse_date(data.get('available_date'), 'available_date')
        except ValueError as ex:
            return jsonify({'message': str(ex)}), 400
    if 'start_time' in data:
        avail.start_time = (data.get('start_time') or '').strip()
    if 'end_time' in data:
        avail.end_time = (data.get('end_time') or '').strip()
    if avail.start_time and avail.end_time and avail.start_time >= avail.end_time:
        return jsonify({'message': 'start_time must be before end_time.'}), 400
    if 'max_slots' in data:
        avail.max_slots = data.get('max_slots') or avail.max_slots
    db.session.commit()
    return jsonify({'availability': {
        'id': avail.id,
        'available_date': avail.available_date.isoformat(),
        'start_time': avail.start_time,
        'end_time': avail.end_time,
        'max_slots': avail.max_slots,
    }})


@admin_bp.route('/patients', methods=['GET', 'POST'])
@token_required(roles=['admin'])
def patients(current_user):
    if request.method == 'POST':
        data = request.get_json() or {}
        first_name = (data.get('first_name') or '').strip()
        last_name = (data.get('last_name') or '').strip()
        email = (data.get('email') or '').strip().lower()
        phone = (data.get('phone') or '').strip()
        dob_raw = (data.get('dob') or '').strip()
        gender = (data.get('gender') or '').strip()
        password = (data.get('password') or 'Patient@1234')

        missing = [k for k in ['first_name', 'last_name', 'email', 'phone', 'dob', 'gender'] if not data.get(k)]
        if missing:
            return jsonify({'message': f'Missing fields: {", ".join(missing)}'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'An account with this email already exists.'}), 409
        if Patient.query.filter_by(phone=phone).first():
            return jsonify({'message': 'An account with this phone number already exists.'}), 409

        try:
            dob = _parse_date(dob_raw, 'dob')
        except ValueError as ex:
            return jsonify({'message': str(ex)}), 400
        if not dob:
            return jsonify({'message': 'Invalid date of birth.'}), 400

        insurance_coverage_start = None
        if data.get('insurance_coverage_start'):
            try:
                insurance_coverage_start = _parse_date(data.get('insurance_coverage_start'), 'insurance_coverage_start')
            except ValueError as ex:
                return jsonify({'message': str(ex)}), 400

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
            gender=gender,
            address=_clean_optional(data.get('address')),
            emergency_contact_name=_clean_optional(data.get('emergency_contact_name')),
            emergency_contact_relationship=_clean_optional(data.get('emergency_contact_relationship')),
            emergency_contact_phone=_clean_optional(data.get('emergency_contact_phone')),
            insurance_provider=_clean_optional(data.get('insurance_provider')),
            insurance_policy_number=_clean_optional(data.get('insurance_policy_number')),
            insurance_member_id=_clean_optional(data.get('insurance_member_id')),
            insurance_coverage_start=insurance_coverage_start,
            allergies=_clean_optional(data.get('allergies')),
            medications=_clean_optional(data.get('medications')),
            conditions=_clean_optional(data.get('conditions')),
            primary_physician=_clean_optional(data.get('primary_physician')),
            preferred_language=_clean_optional(data.get('preferred_language')),
            communication_preferences=_clean_optional(data.get('communication_preferences')),
            accessibility_needs=_clean_optional(data.get('accessibility_needs')),
            occupation=_clean_optional(data.get('occupation')),
            marital_status=_clean_optional(data.get('marital_status')),
            blood_type=_clean_optional(data.get('blood_type')),
            family_history=_clean_optional(data.get('family_history')),
            pregnancy_status=_clean_optional(data.get('pregnancy_status')),
            preferred_pharmacy=_clean_optional(data.get('preferred_pharmacy')),
            consent_terms=bool(data.get('consent_terms')),
            consent_telehealth=bool(data.get('consent_telehealth')),
            consent_reminders=bool(data.get('consent_reminders')),
            consent_marketing=bool(data.get('consent_marketing')),
            government_id_type=_clean_optional(data.get('government_id_type')),
            government_id_number=_clean_optional(data.get('government_id_number')),
        )
        db.session.add(patient)
        db.session.commit()

        credentials_sent = False
        if email:
            subject = 'Your Patient Account Credentials'
            body = (
                f'Hello {first_name},\n\n'
                f'Your patient account has been created.\n'
                f'Login email: {email}\n'
                f'Temporary password: {password}\n\n'
                f'Please log in and change your password after first login.'
            )
            credentials_sent = _send_email(email, subject, body)

        return jsonify({
            'patient': patient_to_dict(patient),
            'temp_password': password,
            'credentials_email_sent': credentials_sent
        }), 201

    q = (request.args.get('q') or '').strip().lower()
    dept_id = (request.args.get('department_id') or '').strip()
    query = Patient.query
    if q:
        query = query.join(User, Patient.user_id == User.id).filter(
            (Patient.patient_uid.ilike(f'%{q}%')) |
            (Patient.first_name.ilike(f'%{q}%')) |
            (Patient.last_name.ilike(f'%{q}%')) |
            (Patient.phone.ilike(f'%{q}%')) |
            (User.email.ilike(f'%{q}%'))
        )
    if dept_id:
        try:
            dept_id_int = int(dept_id)
            query = query.join(Appointment, Appointment.patient_id == Patient.id) \
                .join(Doctor, Appointment.doctor_id == Doctor.id) \
                .filter(Doctor.department_id == dept_id_int) \
                .distinct()
        except ValueError:
            pass
    patients = query.order_by(Patient.created_at.desc()).all()

    payload = []
    for p in patients:
        pd = patient_to_dict(p)
        pd['is_blacklisted'] = p.user.is_blacklisted if p.user else False
        payload.append(pd)
    return jsonify({'patients': payload})


@admin_bp.route('/patients/lookup', methods=['GET'])
@token_required(roles=['admin'])
def lookup_patient(current_user):
    q = request.args.get('uid', '').strip()
    if not q:
        return jsonify({'message': 'Patient UID is required'}), 400
    
    patient = Patient.query.filter(Patient.patient_uid == q).first()
    if not patient and q.isdigit():
        patient = Patient.query.filter(Patient.id == int(q)).first()
        
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404
        
    pd = patient_to_dict(patient)
    if patient.user:
        pd['email'] = patient.user.email
    return jsonify({'patient': pd})


@admin_bp.route('/patients/<int:patient_id>/blacklist', methods=['PATCH'])
@token_required(roles=['admin'])
def patient_blacklist(current_user, patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if patient.user:
        data = request.get_json() or {}
        target_status = data.get('blacklist', not patient.user.is_blacklisted)
        patient.user.is_blacklisted = target_status
        db.session.commit()
        return jsonify({'message': 'Patient blacklisted' if target_status else 'Patient activated'})
    return jsonify({'message': 'No user attached'}), 400


@admin_bp.route('/patients/<int:patient_id>', methods=['PUT', 'DELETE'])
@token_required(roles=['admin'])
def patient_detail(current_user, patient_id):
    patient = Patient.query.get_or_404(patient_id)
    user = patient.user

    if request.method == 'DELETE':
        has_appointments = Appointment.query.filter_by(patient_id=patient.id).first() is not None
        if has_appointments:
            return jsonify({'message': 'Cannot delete patient with existing appointments. Use blacklist instead.'}), 409
        if user:
            db.session.delete(user)
        db.session.delete(patient)
        db.session.commit()
        return jsonify({'message': 'Patient deleted'})

    data = request.get_json() or {}
    if 'first_name' in data:
        first_name = (data.get('first_name') or '').strip()
        if not first_name:
            return jsonify({'message': 'First name cannot be empty.'}), 400
        patient.first_name = first_name
    if 'last_name' in data:
        last_name = (data.get('last_name') or '').strip()
        if not last_name:
            return jsonify({'message': 'Last name cannot be empty.'}), 400
        patient.last_name = last_name
    if 'phone' in data:
        phone = (data.get('phone') or '').strip()
        if not phone:
            return jsonify({'message': 'Phone cannot be empty.'}), 400
        phone_owner = Patient.query.filter(Patient.phone == phone, Patient.id != patient.id).first()
        if phone_owner:
            return jsonify({'message': 'Phone already exists.'}), 409
        patient.phone = phone
    if 'dob' in data:
        try:
            dob = _parse_date(data.get('dob'), 'date of birth')
        except ValueError as ex:
            return jsonify({'message': str(ex)}), 400
        if not dob:
            return jsonify({'message': 'Date of birth cannot be empty.'}), 400
        patient.dob = dob
    if 'gender' in data:
        gender = (data.get('gender') or '').strip()
        if not gender:
            return jsonify({'message': 'Gender cannot be empty.'}), 400
        patient.gender = gender
    if 'address' in data:
        patient.address = _clean_optional(data.get('address'))
    if 'emergency_contact_name' in data:
        patient.emergency_contact_name = _clean_optional(data.get('emergency_contact_name'))
    if 'emergency_contact_relationship' in data:
        patient.emergency_contact_relationship = _clean_optional(data.get('emergency_contact_relationship'))
    if 'emergency_contact_phone' in data:
        patient.emergency_contact_phone = _clean_optional(data.get('emergency_contact_phone'))
    if 'insurance_provider' in data:
        patient.insurance_provider = _clean_optional(data.get('insurance_provider'))
    if 'insurance_policy_number' in data:
        patient.insurance_policy_number = _clean_optional(data.get('insurance_policy_number'))
    if 'insurance_member_id' in data:
        patient.insurance_member_id = _clean_optional(data.get('insurance_member_id'))
    if 'insurance_coverage_start' in data:
        try:
            patient.insurance_coverage_start = _parse_date(data.get('insurance_coverage_start'), 'insurance coverage start')
        except ValueError as ex:
            return jsonify({'message': str(ex)}), 400
    if 'allergies' in data:
        patient.allergies = _clean_optional(data.get('allergies'))
    if 'medications' in data:
        patient.medications = _clean_optional(data.get('medications'))
    if 'conditions' in data:
        patient.conditions = _clean_optional(data.get('conditions'))
    if 'primary_physician' in data:
        patient.primary_physician = _clean_optional(data.get('primary_physician'))
    if 'preferred_language' in data:
        patient.preferred_language = _clean_optional(data.get('preferred_language'))
    if 'communication_preferences' in data:
        patient.communication_preferences = _clean_optional(data.get('communication_preferences'))
    if 'accessibility_needs' in data:
        patient.accessibility_needs = _clean_optional(data.get('accessibility_needs'))
    if 'occupation' in data:
        patient.occupation = _clean_optional(data.get('occupation'))
    if 'marital_status' in data:
        patient.marital_status = _clean_optional(data.get('marital_status'))
    if 'blood_type' in data:
        patient.blood_type = _clean_optional(data.get('blood_type'))
    if 'family_history' in data:
        patient.family_history = _clean_optional(data.get('family_history'))
    if 'pregnancy_status' in data:
        patient.pregnancy_status = _clean_optional(data.get('pregnancy_status'))
    if 'preferred_pharmacy' in data:
        patient.preferred_pharmacy = _clean_optional(data.get('preferred_pharmacy'))
    if 'government_id_type' in data:
        patient.government_id_type = _clean_optional(data.get('government_id_type'))
    if 'government_id_number' in data:
        patient.government_id_number = _clean_optional(data.get('government_id_number'))
    if 'consent_terms' in data:
        patient.consent_terms = bool(data.get('consent_terms'))
    if 'consent_telehealth' in data:
        patient.consent_telehealth = bool(data.get('consent_telehealth'))
    if 'consent_reminders' in data:
        patient.consent_reminders = bool(data.get('consent_reminders'))
    if 'consent_marketing' in data:
        patient.consent_marketing = bool(data.get('consent_marketing'))
    if 'email' in data and user:
        email = (data.get('email') or '').strip().lower()
        if not email:
            return jsonify({'message': 'Email cannot be empty.'}), 400
        existing_user = User.query.filter(User.email == email, User.id != user.id).first()
        if existing_user:
            return jsonify({'message': 'Email already exists.'}), 409
        user.email = email

    db.session.commit()
    return jsonify({'patient': patient_to_dict(patient)})


@admin_bp.route('/appointments', methods=['GET', 'POST'])
@token_required(roles=['admin'])
def appointments(current_user):
    if request.method == 'POST':
        data = request.get_json() or {}
        doctor_id = data.get('doctor_id')
        patient_id = data.get('patient_id')
        appointment_dt = parse_dt(data.get('appointment_dt'))
        if not doctor_id or not patient_id or not appointment_dt:
            return jsonify({'message': 'doctor_id, patient_id and appointment_dt are required (YYYY-MM-DD HH:MM).'}), 400

        doctor = Doctor.query.get(doctor_id)
        patient = Patient.query.get(patient_id)
        if not doctor:
            return jsonify({'message': 'Doctor not found.'}), 404
        if not patient:
            return jsonify({'message': 'Patient not found.'}), 404

        # Availability check for requested time slot
        target_date = appointment_dt.date()
        slots = compute_slots_for_doctor_date(doctor_id, target_date)
        time_key = appointment_dt.strftime('%H:%M')
        slot = next((s for s in slots if s.get('time') == time_key), None)
        if not slot or not slot.get('available'):
            return jsonify({'message': 'No available slots for this time.'}), 409

        # Prevent double booking for same doctor at same time
        conflict = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_dt=appointment_dt,
            status='booked'
        ).first()
        if conflict:
            return jsonify({'message': 'This time slot is already booked.'}), 409

        appt = Appointment(
            doctor_id=doctor_id,
            patient_id=patient_id,
            appointment_dt=appointment_dt,
            status='booked',
        )
        db.session.add(appt)
        db.session.flush()
        year_tag = appointment_dt.strftime('%y') if appointment_dt else None
        appt.appointment_uid = Appointment.format_appointment_uid(appt.id, year_tag)
        db.session.commit()
        return jsonify({'appointment': appointment_to_dict(appt)}), 201

    status = (request.args.get('status') or '').strip().lower()
    query = Appointment.query
    if status:
        query = query.filter_by(status=status)
    appts = query.order_by(Appointment.appointment_dt.desc()).all()
    return jsonify({'appointments': [appointment_to_dict(a) for a in appts]})


@admin_bp.route('/available-slots', methods=['GET'])
@token_required(roles=['admin'])
def admin_available_slots(current_user):
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


@admin_bp.route('/booking/doctors-on-date', methods=['GET'])
@token_required(roles=['admin'])
def admin_booking_doctors_on_date(current_user):
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

    query = Doctor.query
    if spec:
        query = query.filter(Doctor.specialization.ilike(f'%{spec}%'))
    if department_id:
        query = query.filter(Doctor.department_id == department_id)
    doctors = query.order_by(Doctor.name).all()

    payload = [doctor_to_dict(d) for d in doctors if doctor_has_free_slot(d.id, target_date)]
    return jsonify({'doctors': payload})


@admin_bp.route('/patients/<int:patient_id>/appointments', methods=['GET'])
@token_required(roles=['admin'])
def patient_appointments(current_user, patient_id):
    Patient.query.get_or_404(patient_id)
    appts = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.appointment_dt.desc()).all()
    return jsonify({'appointments': [appointment_to_dict(a) for a in appts]})


@admin_bp.route('/appointments/<int:appointment_id>/transfer', methods=['POST'])
@token_required(roles=['admin'])
def transfer_appointment(current_user, appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)
    data = request.get_json() or {}
    target_doctor_id = data.get('doctor_id')
    if not target_doctor_id:
        return jsonify({'message': 'doctor_id is required.'}), 400
    if (appt.status or '').lower() != 'booked':
        return jsonify({'message': 'Only booked appointments can be transferred.'}), 400
    target_doc = Doctor.query.get(target_doctor_id)
    if not target_doc:
        return jsonify({'message': 'Doctor not found.'}), 404

    # Availability check for the appointment datetime
    appt_date = appt.appointment_dt.date()
    appt_time = appt.appointment_dt.strftime('%H:%M')
    avails = DoctorAvailability.query.filter_by(doctor_id=target_doc.id, available_date=appt_date).all()
    if not avails:
        return jsonify({'message': 'Doctor has no availability on this date.'}), 409

    def within_slot(slot):
        return slot.start_time <= appt_time < slot.end_time

    matching = [a for a in avails if within_slot(a)]
    if not matching:
        return jsonify({'message': 'Doctor is not available at the appointment time.'}), 409

    # capacity check for the exact time
    booked_count = Appointment.query.filter_by(
        doctor_id=target_doc.id,
        appointment_dt=appt.appointment_dt,
        status='booked'
    ).count()
    max_slots = max(a.max_slots for a in matching)
    if booked_count >= max_slots:
        return jsonify({'message': 'No available slots for this time.'}), 409

    appt.doctor_id = target_doc.id
    db.session.commit()
    return jsonify({'appointment': appointment_to_dict(appt)})


@admin_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@token_required(roles=['admin'])
def update_appointment(current_user, appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)
    data = request.get_json() or {}
    
    if 'status' in data:
        status = (data['status'] or '').strip().lower()
        allowed_statuses = {'booked', 'completed', 'cancelled'}
        if status not in allowed_statuses:
            return jsonify({'message': f'Invalid status. Allowed: {", ".join(sorted(allowed_statuses))}.'}), 400
        appt.status = status
    
    if 'appointment_dt' in data:
        appointment_dt = parse_dt((data.get('appointment_dt') or '').strip())
        if not appointment_dt:
            return jsonify({'message': 'Invalid appointment_dt. Use YYYY-MM-DD HH:MM.'}), 400
        
        # Check for conflicts if rescheduling
        conflict = Appointment.query.filter_by(
            doctor_id=appt.doctor_id,
            appointment_dt=appointment_dt,
            status='booked'
        ).first()
        if conflict and conflict.id != appt.id:
            return jsonify({'message': 'This time slot is already booked.'}), 409
        
        appt.appointment_dt = appointment_dt
    
    db.session.commit()
    return jsonify({'appointment': appointment_to_dict(appt)})


@admin_bp.route('/jobs/daily-reminders', methods=['POST'])
@token_required(roles=['admin'])
def run_daily_reminders(current_user):
    from ..jobs.tasks import daily_reminders
    task = daily_reminders.apply_async()
    return jsonify({'message': 'Daily reminder job queued', 'task_id': task.id})


@admin_bp.route('/jobs/monthly-report', methods=['POST'])
@token_required(roles=['admin'])
def run_monthly_report(current_user):
    from ..jobs.tasks import monthly_report
    task = monthly_report.apply_async()
    return jsonify({'message': 'Monthly report job queued', 'task_id': task.id})


@admin_bp.route('/reports', methods=['GET'])
@token_required(roles=['admin'])
def list_all_reports(current_user):
    doctor_id = request.args.get('doctor_id', type=int)
    query = MonthlyReport.query
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    reports = query.order_by(MonthlyReport.generated_at.desc()).all()
    return jsonify({'reports': [monthly_report_to_dict(r) for r in reports]})


@admin_bp.route('/doctors/<int:doctor_id>/generate-report', methods=['POST'])
@token_required(roles=['admin'])
def admin_trigger_instant_report(current_user, doctor_id):
    from ..jobs.tasks import generate_instant_doctor_report
    result = generate_instant_doctor_report(doctor_id)
    return jsonify(result)


@admin_bp.route('/reports/<int:report_id>/download', methods=['GET'])
@token_required(roles=['admin'])
def download_admin_report(current_user, report_id):
    report = MonthlyReport.query.get_or_404(report_id)
    return send_file(report.file_path, mimetype='text/html', as_attachment=True, download_name=f'Report_{report.report_month.replace(" ", "_")}.html')
