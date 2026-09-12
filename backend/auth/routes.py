"""
backend/auth/routes.py
Flask auth blueprint — handles login/register for all three roles.
Register this blueprint in your app factory with:
    from auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from functools import wraps
import jwt

from ..models import db, User, Patient, Doctor

auth_bp = Blueprint('auth', __name__)


def is_strong_password(password: str) -> bool:
    pwd = str(password or '')
    return (
        len(pwd) >= 8
        and any(c.islower() for c in pwd)
        and any(c.isupper() for c in pwd)
        and any(c.isdigit() for c in pwd)
        and any(not c.isalnum() for c in pwd)
    )


# ─────────────────────────────────────────────
# Helper: generate JWT token
# ─────────────────────────────────────────────
def generate_token(user_id: int, role: str) -> str:
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


# ─────────────────────────────────────────────
# Helper: decode & verify JWT (used as decorator)
# ─────────────────────────────────────────────
def token_required(roles=None):
    """
    Decorator to protect routes.
    Usage:
        @auth_bp.route('/some-protected')
        @token_required(roles=['admin'])
        def some_view(current_user):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({'message': 'Missing or malformed token'}), 401
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token expired. Please log in again.'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Invalid token.'}), 401

            if roles and payload['role'] not in roles:
                return jsonify({'message': 'Access denied: insufficient permissions.'}), 403

            current_user = User.query.get(payload['user_id'])
            if not current_user or current_user.is_blacklisted:
                return jsonify({'message': 'Account suspended or not found.'}), 403

            return f(current_user, *args, **kwargs)
        return decorated
    return decorator


# ─────────────────────────────────────────────
# POST /api/auth/patient/register
# ─────────────────────────────────────────────
@auth_bp.route('/patient/register', methods=['POST'])
def patient_register():
    data = request.get_json() or {}

    required = ['first_name', 'last_name', 'email', 'password', 'phone', 'dob', 'gender']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'message': f'Missing fields: {", ".join(missing)}'}), 400
    if data.get('consent_terms') is not True:
        return jsonify({'message': 'You must accept the terms and privacy policy to register.'}), 400

    # Email uniqueness check
    email = data['email'].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'An account with this email already exists.'}), 409

    # Phone uniqueness check
    if Patient.query.filter_by(phone=data['phone']).first():
        return jsonify({'message': 'An account with this phone number already exists.'}), 409

    if not is_strong_password(data['password']):
        return jsonify({
            'message': 'Password must be 8+ chars and include uppercase, lowercase, number, and special character.'
        }), 400

    try:
        dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    insurance_coverage_start = None
    if data.get('insurance_coverage_start'):
        try:
            insurance_coverage_start = datetime.strptime(
                data['insurance_coverage_start'],
                '%Y-%m-%d'
            ).date()
        except ValueError:
            return jsonify({'message': 'Invalid insurance coverage date. Use YYYY-MM-DD.'}), 400

    user = User(
        email=email,
        password_hash=generate_password_hash(data['password']),
        role='patient',
        is_active=True
    )
    db.session.add(user)
    db.session.flush()  # get user.id without committing

    patient = Patient(
        user_id=user.id,
        patient_uid=Patient.generate_patient_uid(),
        first_name=data['first_name'].strip(),
        last_name=data['last_name'].strip(),
        phone=data['phone'],
        dob=dob,
        gender=data['gender'],
        address=data.get('address'),
        emergency_contact_name=data.get('emergency_contact_name'),
        emergency_contact_relationship=data.get('emergency_contact_relationship'),
        emergency_contact_phone=data.get('emergency_contact_phone'),
        insurance_provider=data.get('insurance_provider'),
        insurance_policy_number=data.get('insurance_policy_number'),
        insurance_member_id=data.get('insurance_member_id'),
        insurance_coverage_start=insurance_coverage_start,
        allergies=data.get('allergies'),
        medications=data.get('medications'),
        conditions=data.get('conditions'),
        primary_physician=data.get('primary_physician'),
        preferred_language=data.get('preferred_language'),
        communication_preferences=data.get('communication_preferences'),
        accessibility_needs=data.get('accessibility_needs'),
        occupation=data.get('occupation'),
        marital_status=data.get('marital_status'),
        blood_type=data.get('blood_type'),
        family_history=data.get('family_history'),
        pregnancy_status=data.get('pregnancy_status'),
        preferred_pharmacy=data.get('preferred_pharmacy'),
        consent_terms=bool(data.get('consent_terms')),
        consent_telehealth=bool(data.get('consent_telehealth')),
        consent_reminders=bool(data.get('consent_reminders')),
        consent_marketing=bool(data.get('consent_marketing')),
        government_id_type=data.get('government_id_type'),
        government_id_number=data.get('government_id_number')
    )
    db.session.add(patient)
    db.session.commit()

    return jsonify({'message': 'Account created successfully. Please log in.'}), 201


# ─────────────────────────────────────────────
# GET /api/auth/check
# Public — real-time uniqueness check for registration
# Query params: ?email=...  &/or  ?phone=...
# Returns: { email_taken: bool, phone_taken: bool }
# ─────────────────────────────────────────────
@auth_bp.route('/check', methods=['GET'])
def check_uniqueness():
    email = (request.args.get('email') or '').strip().lower()
    phone = (request.args.get('phone') or '').strip()

    result = {}
    if email:
        result['email_taken'] = User.query.filter_by(email=email).first() is not None
    if phone:
        result['phone_taken'] = Patient.query.filter_by(phone=phone).first() is not None

    return jsonify(result), 200


# ─────────────────────────────────────────────
# POST /api/auth/patient/login
# ─────────────────────────────────────────────
@auth_bp.route('/patient/login', methods=['POST'])
def patient_login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'message': 'Email and password are required.'}), 400

    user = User.query.filter_by(email=email, role='patient').first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid email or password.'}), 401

    if user.is_blacklisted:
        return jsonify({'message': 'You are blacklisted.'}), 403

    patient = Patient.query.filter_by(user_id=user.id).first()
    token = generate_token(user.id, 'patient')

    return jsonify({
        'token': token,
        'role': 'patient',
        'user': {
            'id': user.id,
            'email': user.email,
            'patient_uid': patient.patient_uid if patient else None,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
        }
    }), 200


# ─────────────────────────────────────────────
# POST /api/auth/doctor/login
# ─────────────────────────────────────────────
@auth_bp.route('/doctor/login', methods=['POST'])
def doctor_login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'message': 'Email and password are required.'}), 400

    user = User.query.filter_by(email=email, role='doctor').first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid credentials. Contact admin if this is unexpected.'}), 401

    if user.is_blacklisted:
        return jsonify({'message': 'You are blacklisted.'}), 403

    doctor = Doctor.query.filter_by(user_id=user.id).first()
    token = generate_token(user.id, 'doctor')

    return jsonify({
        'token': token,
        'role': 'doctor',
        'user': {
            'id': user.id,
            'email': user.email,
            'name': doctor.name,
            'specialization': doctor.specialization
        }
    }), 200


# ─────────────────────────────────────────────
# POST /api/auth/admin/login
# ─────────────────────────────────────────────
@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'message': 'Username and password are required.'}), 400

    # Admin is identified by username (stored in User.username) + role='admin'
    user = User.query.filter_by(username=username, role='admin').first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid admin credentials.'}), 401

    token = generate_token(user.id, 'admin')

    return jsonify({
        'token': token,
        'role': 'admin',
        'user': {
            'id': user.id,
            'username': user.username,
        }
    }), 200


# ─────────────────────────────────────────────
# POST /api/auth/logout
# ─────────────────────────────────────────────
@auth_bp.route('/logout', methods=['POST'])
@token_required()
def logout(current_user):
    # If you add a token blacklist table later, invalidate the token here.
    # For now, logout is handled client-side by clearing localStorage.
    return jsonify({'message': 'Logged out successfully.'}), 200


# ─────────────────────────────────────────────
# GET /api/auth/me
# ─────────────────────────────────────────────
@auth_bp.route('/me', methods=['GET'])
@token_required()
def get_current_user(current_user):
    """Returns the current user's info from token. Used on app load to restore session."""
    data = {
        'id': current_user.id,
        'email': current_user.email,
        'role': current_user.role
    }
    if current_user.role == 'patient':
        p = Patient.query.filter_by(user_id=current_user.id).first()
        if p:
            data.update({'first_name': p.first_name, 'last_name': p.last_name})
    elif current_user.role == 'doctor':
        d = Doctor.query.filter_by(user_id=current_user.id).first()
        if d:
            data.update({'name': d.name, 'specialization': d.specialization})
    elif current_user.role == 'admin':
        data['username'] = current_user.username

    return jsonify(data), 200
