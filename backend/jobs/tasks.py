from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
import os
import json
import urllib.request
import urllib.error
import smtplib
from email.message import EmailMessage
import csv
import io
from .celery_app import celery_app
from ..models import db, Appointment, Patient, Doctor, User, MonthlyReport

# Basic stubs for required background jobs.
# Hook these into real email/SMS/Chat systems later.

def _send_google_chat(message: str) -> bool:
    webhook_url = os.environ.get('GOOGLE_CHAT_WEBHOOK_URL', '').strip()
    if not webhook_url:
        return False
    payload = json.dumps({'text': message}).encode('utf-8')
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, urllib.error.HTTPError):
        return False


def _send_email(to_email: str, subject: str, body: str, html: str | None = None) -> bool:
    host = os.environ.get('SMTP_HOST', '').strip()
    user = os.environ.get('SMTP_USER', '').strip()
    password = os.environ.get('SMTP_PASSWORD', '').strip()
    sender = os.environ.get('SMTP_SENDER', '').strip() or user
    if not host or not sender:
        return False
    port = int(os.environ.get('SMTP_PORT', '587'))

    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype='html')

    try:
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.starttls()
            if user and password:
                server.login(user, password)
            server.send_message(msg)
        return True
    except Exception:
        return False


def _send_reminder(message: str, email: str | None, phone: str | None = None) -> str:
    channels = []
    # 1. Google Chat
    if _send_google_chat(message):
        channels.append('chat')
    
    # 2. Email
    if email and _send_email(email, 'Appointment Reminder — CareSync Hospital', message):
        channels.append('email')
    
    # 3. SMS (Log fallback/stub)
    if phone:
        print(f'[HMS SMS Reminder] Sent to {phone}: {message}')
        channels.append('sms-log')
    
    if not channels:
        print(f'[HMS Reminder Fallback] {message}')
        return 'log'
    
    return ','.join(channels)


@celery_app.task
def daily_reminders():
    from ..app import create_app
    app = create_app()
    tz = ZoneInfo(os.environ.get('APP_TIMEZONE', 'Asia/Kolkata'))
    now = datetime.now(tz)
    target_date = now.date()
    start_dt = datetime.combine(target_date, time.min)
    end_dt = datetime.combine(target_date, time.max)
    sent = []

    with app.app_context():
        # Find all 'booked' appointments for today
        appts = Appointment.query.filter(
            Appointment.appointment_dt >= start_dt,
            Appointment.appointment_dt <= end_dt,
            Appointment.status == 'booked'
        ).all()
        
        for appt in appts:
            patient = Patient.query.get(appt.patient_id)
            doctor = Doctor.query.get(appt.doctor_id)
            if not patient or not doctor:
                continue
            
            user = User.query.get(patient.user_id) if patient.user_id else None
            
            # Note: consent_reminders check REMOVED per user request (reminders are compulsory)
            
            appt_time = appt.appointment_dt.strftime('%I:%M %p')
            appt_date = appt.appointment_dt.strftime('%b %d, %Y')
            
            message = (
                f"Good morning {patient.first_name},\n\n"
                f"This is a reminder for your scheduled visit to CareSync Hospital today.\n"
                f"Appointment: {appt_date} at {appt_time}\n"
                f"Provider: Dr. {doctor.name} ({doctor.specialization})\n\n"
                f"Please arrive 15 minutes before your scheduled time. If you need to reschedule, please contact us."
            )
            
            # Send to all available channels
            channel = _send_reminder(
                message, 
                user.email if user else None,
                patient.phone
            )
            
            sent.append({
                'patient_id': patient.id,
                'doctor_id': doctor.id,
                'appointment_id': appt.id,
                'channel': channel,
            })

    return {
        'status': 'ok',
        'message': 'Daily reminders processed',
        'run_at': now.isoformat(),
        'appointments_checked': len(sent),
        'sent': sent[:50],
    }


def _generate_doctor_report_content(doctor, start_dt, end_dt, report_month):
    """
    Common logic to generate the HTML report content.
    """
    appts = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_dt >= start_dt,
        Appointment.appointment_dt <= end_dt,
    ).order_by(Appointment.appointment_dt.asc()).all()

    def appt_uid(appt):
        if appt.appointment_uid:
            return appt.appointment_uid
        yy = appt.appointment_dt.strftime('%y') if appt.appointment_dt else start_dt.strftime('%y')
        return f'CS{yy}A{int(appt.id):04d}'

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

    html_rows = ''.join([
        f'''
        <tr>
          <td style="border-bottom:1px solid #e2e8f0;padding:8px">{r["appointment_uid"]}</td>
          <td style="border-bottom:1px solid #e2e8f0;padding:8px">{r["date"]}</td>
          <td style="border-bottom:1px solid #e2e8f0;padding:8px">{r["time"]}</td>
          <td style="border-bottom:1px solid #e2e8f0;padding:8px">{r["patient"]}</td>
          <td style="border-bottom:1px solid #e2e8f0;padding:8px">{r["status"].title()}</td>
          <td style="border-bottom:1px solid #e2e8f0;padding:8px">{r["diagnosis"] or '-'}</td>
          <td style="border-bottom:1px solid #e2e8f0;padding:8px">{r["prescription"] or '-'}</td>
          <td style="border-bottom:1px solid #e2e8f0;padding:8px">{r["notes"] or '-'}</td>
        </tr>
        ''' for r in rows
    ]) or '<tr><td colspan="8" style="padding:12px;color:#64748b;text-align:center">No appointments recorded.</td></tr>'

    html = f"""
    <html>
      <body style="font-family:Arial,Helvetica,sans-serif;color:#0f172a;background:#f8fafc;padding:20px">
        <div style="max-width:1000px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:30px;box-shadow:0 4px 6px -1px rgb(0 0 0 / 0.1)">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;border-bottom:2px solid #3b82f6;padding-bottom:16px">
            <h1 style="margin:0;color:#1e40af;font-size:24px">Monthly Activity Report</h1>
            <div style="text-align:right">
                <div style="font-weight:bold;color:#334155">{report_month}</div>
                <div style="font-size:12px;color:#64748b">Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}</div>
            </div>
          </div>
          
          <div style="margin-bottom:24px;background:#f1f5f9;padding:16px;border-radius:8px;display:grid;grid-template-columns:1fr 1fr;gap:16px">
            <div><strong>Doctor:</strong> Dr. {doctor.name}</div>
            <div><strong>Specialization:</strong> {doctor.specialization}</div>
            <div><strong>Period:</strong> {start_dt.strftime('%b %d')} - {end_dt.strftime('%b %d, %Y')}</div>
            <div><strong>Total Appointments:</strong> {len(rows)}</div>
          </div>

          <table style="width:100%;border-collapse:collapse;font-size:13px">
            <thead>
              <tr style="background:#f8fafc">
                <th style="text-align:left;border-bottom:2px solid #e2e8f0;padding:12px;color:#475569">Appt ID</th>
                <th style="text-align:left;border-bottom:2px solid #e2e8f0;padding:12px;color:#475569">Date</th>
                <th style="text-align:left;border-bottom:2px solid #e2e8f0;padding:12px;color:#475569">Time</th>
                <th style="text-align:left;border-bottom:2px solid #e2e8f0;padding:12px;color:#475569">Patient</th>
                <th style="text-align:left;border-bottom:2px solid #e2e8f0;padding:12px;color:#475569">Status</th>
                <th style="text-align:left;border-bottom:2px solid #e2e8f0;padding:12px;color:#475569">Diagnosis</th>
                <th style="text-align:left;border-bottom:2px solid #e2e8f0;padding:12px;color:#475569">Prescription</th>
                <th style="text-align:left;border-bottom:2px solid #e2e8f0;padding:12px;color:#475569">Notes</th>
              </tr>
            </thead>
            <tbody>
              {html_rows}
            </tbody>
          </table>
          
          <div style="margin-top:40px;padding-top:20px;border-top:1px solid #e2e8f0;font-size:12px;color:#94a3b8;text-align:center">
            This is an automated report from CareSync Hospital Management System.
          </div>
        </div>
      </body>
    </html>
    """
    return html, len(rows)


@celery_app.task
def monthly_report():
    from ..app import create_app
    app = create_app()
    tz = ZoneInfo(os.environ.get('APP_TIMEZONE', 'Asia/Kolkata'))
    now = datetime.now(tz)
    
    # Run logic for the current month up to now (scheduled for the 30th)
    start_dt = datetime(now.year, now.month, 1)
    end_dt = datetime(now.year, now.month, now.day, 23, 59, 59)
    report_month_name = now.strftime("%B %Y")

    sent = []
    with app.app_context():
        doctors = Doctor.query.all()
        for doctor in doctors:
            user = User.query.get(doctor.user_id) if doctor.user_id else None
            to_email = user.email if user and user.email else ''
            
            html, count = _generate_doctor_report_content(doctor, start_dt, end_dt, report_month_name)
            
            # Save report to file
            reports_dir = os.path.join(app.instance_path, 'reports', f'doctor_{doctor.id}')
            os.makedirs(reports_dir, exist_ok=True)
            filename = f'monthly_report_{now.strftime("%Y%m%d_%H%M%S")}.html'
            file_path = os.path.join(reports_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            # Record in DB
            report_rec = MonthlyReport(
                doctor_id=doctor.id,
                report_month=report_month_name,
                file_path=file_path,
                generated_at=datetime.utcnow()
            )
            db.session.add(report_rec)
            db.session.commit()

            if to_email:
                subject = f'Monthly Activity Report — {report_month_name}'
                plain = f'Monthly Activity Report for Dr. {doctor.name} ({report_month_name}). Appointments: {count}.'
                _send_email(to_email, subject, plain, html=html)
                sent.append({'doctor_id': doctor.id, 'email': to_email, 'appointments': count})

    return {
        'status': 'ok',
        'message': 'Monthly reports processed and saved',
        'run_at': now.isoformat(),
        'sent': sent,
    }


@celery_app.task
def generate_instant_doctor_report(doctor_id):
    from ..app import create_app
    app = create_app()
    tz = ZoneInfo(os.environ.get('APP_TIMEZONE', 'Asia/Kolkata'))
    now = datetime.now(tz)
    
    start_dt = datetime(now.year, now.month, 1)
    end_dt = datetime(now.year, now.month, now.day, 23, 59, 59)
    report_month_name = now.strftime("%B %Y (Instant)")

    with app.app_context():
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return {'status': 'failed', 'message': 'Doctor not found'}
            
        user = User.query.get(doctor.user_id) if doctor.user_id else None
        to_email = user.email if user and user.email else ''
        
        html, count = _generate_doctor_report_content(doctor, start_dt, end_dt, report_month_name)
        
        # Save report to file
        reports_dir = os.path.join(app.instance_path, 'reports', f'doctor_{doctor.id}')
        os.makedirs(reports_dir, exist_ok=True)
        filename = f'instant_report_{now.strftime("%Y%m%d_%H%M%S")}.html'
        file_path = os.path.join(reports_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Record in DB
        report_rec = MonthlyReport(
            doctor_id=doctor.id,
            report_month=report_month_name,
            file_path=file_path,
            generated_at=datetime.utcnow()
        )
        db.session.add(report_rec)
        db.session.commit()

        if to_email:
            subject = f'Activity Report — {report_month_name}'
            plain = f'Activity Report for Dr. {doctor.name} ({report_month_name}). Appointments: {count}.'
            _send_email(to_email, subject, plain, html=html)

        return {
            'status': 'ok',
            'message': 'Instant report generated and saved',
            'doctor_id': doctor.id,
            'report_id': report_rec.id,
            'appointments': count
        }


@celery_app.task
def export_csv_async(job_id):
    from ..app import create_app
    from ..models import ExportJob, FollowUp

    app = create_app()
    with app.app_context():
        job = ExportJob.query.get(job_id)
        if not job:
            return {'status': 'failed', 'message': 'Export job not found'}

        try:
            job.status = 'processing'
            job.error = None
            db.session.commit()

            patient = Patient.query.get(job.patient_id)
            if not patient:
                job.status = 'failed'
                job.error = 'Patient not found'
                job.completed_at = datetime.utcnow()
                db.session.commit()
                return {'status': 'failed', 'message': job.error}

            user = User.query.get(patient.user_id) if patient.user_id else None

            appts = (
                Appointment.query
                .filter_by(patient_id=patient.id)
                .order_by(Appointment.appointment_dt.asc())
                .all()
            )

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                'patient_id',
                'patient_username',
                'patient_uid',
                'patient_name',
                'consulting_doctor',
                'appointment_id',
                'appointment_uid',
                'appointment_date',
                'diagnosis',
                'treatment_given',
                'prescription',
                'next_visit_date',
                'next_visit_status',
            ])

            for appt in appts:
                treatment = appt.treatment
                follow_up = FollowUp.query.filter_by(source_appointment_id=appt.id).first()
                writer.writerow([
                    patient.id,
                    user.email if user and user.email else '',
                    patient.patient_uid or '',
                    patient.full_name,
                    appt.doctor.name if appt.doctor else '',
                    appt.id,
                    appt.appointment_uid or '',
                    appt.appointment_dt.isoformat() if appt.appointment_dt else '',
                    (treatment.diagnosis or '') if treatment else '',
                    (treatment.notes or '') if treatment else '',
                    (treatment.prescription or '') if treatment else '',
                    follow_up.due_date.isoformat() if follow_up else '',
                    follow_up.status if follow_up else '',
                ])

            csv_content = output.getvalue()
            output.close()

            exports_dir = os.path.join(app.instance_path, 'exports', f'patient_{patient.id}')
            os.makedirs(exports_dir, exist_ok=True)
            filename = f'treatment_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
            file_path = os.path.join(exports_dir, filename)
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(csv_content)

            job.status = 'completed'
            job.record_count = len(appts)
            job.file_path = file_path
            job.completed_at = datetime.utcnow()
            db.session.commit()

            return {
                'status': 'ok',
                'message': 'CSV export completed',
                'job_id': job.id,
                'records': len(appts),
            }
        except Exception as exc:
            job.status = 'failed'
            job.error = str(exc)[:500]
            job.completed_at = datetime.utcnow()
            db.session.commit()
            return {'status': 'failed', 'message': job.error}
