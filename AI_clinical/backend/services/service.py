from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.table_schema import (
    Patient, ClinicalDocument, DischargeSummary, User, 
    DoctorDetails, OTPVerification
)
from fastapi import HTTPException
from services.rag import rag_pipeline
from auth.auth import create_access_token
from database.db import SessionLocal
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random
import string

# ============ INITIALIZATION ============

def init_db():
    """Initialize database with default users"""
    db = SessionLocal()
    
    # Create admin if not exists
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            password="admin123",
            role="admin",
            is_approved=True,
            full_name="System Administrator",
            phone="9999999999",
            email="admin@hospital.com"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    
    # Create doctor if not exists (pending approval)
    doctor = db.query(User).filter(User.username == "dr.smith").first()
    if not doctor:
        doctor = User(
            username="dr.smith",
            password="doctor123",
            role="doctor",
            is_approved=False,
            full_name="Dr. John Smith",
            phone="8888888888",
            email="dr.smith@hospital.com"
        )
        db.add(doctor)
        db.commit()
        db.refresh(doctor)
    
    db.close()

# ============ HELPER FUNCTIONS ============

def generate_employee_id():
    """Generate unique employee ID in format: HYYXXXX"""
    year = datetime.now().strftime("%y")
    random_num = ''.join(random.choices(string.digits, k=4))
    return f"H{year}{random_num}"

def generate_temp_password(length=10):
    """Generate temporary password"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# ============ OTP SERVICES ============

def generate_otp(length=6):
    """Generate numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_sms(phone: str, otp: str):
    """Simulate sending OTP via SMS"""
    print(f"📱 OTP for {phone}: {otp}")
    return True

def send_verification_otp(db: Session, phone: str):
    """Send OTP for phone verification"""
    # Check if phone already exists
    existing_doctor = db.query(DoctorDetails).filter(
        DoctorDetails.phone == phone
    ).first()
    
    if existing_doctor:
        raise HTTPException(
            status_code=400, 
            detail="Phone number already registered with another doctor"
        )
    
    # Delete old OTPs for this phone
    db.query(OTPVerification).filter(
        OTPVerification.phone == phone,
        OTPVerification.verified == False
    ).delete()
    
    # Generate new OTP
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    otp_record = OTPVerification(
        phone=phone,
        otp=otp,
        purpose="registration",
        expires_at=expires_at,
        verified=False,
        attempts=0
    )
    
    db.add(otp_record)
    db.commit()
    
    # Send OTP via SMS
    send_otp_sms(phone, otp)
    
    return {
        "message": "OTP sent successfully",
        "phone": phone,
        "expires_in": 10
    }

def verify_phone_otp(db: Session, phone: str, otp: str):
    """Verify phone OTP"""
    otp_record = db.query(OTPVerification).filter(
        OTPVerification.phone == phone,
        OTPVerification.otp == otp,
        OTPVerification.verified == False,
        OTPVerification.expires_at > datetime.utcnow()
    ).first()
    
    if not otp_record:
        # Record failed attempt
        failed_record = db.query(OTPVerification).filter(
            OTPVerification.phone == phone,
            OTPVerification.verified == False
        ).first()
        if failed_record:
            failed_record.attempts += 1
            db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    # Mark as verified
    otp_record.verified = True
    db.commit()
    
    return {
        "message": "OTP verified successfully",
        "verified": True,
        "phone": phone
    }

# ============ DOCTOR MANAGEMENT ============

def create_doctor_profile(db: Session, doctor_data, admin_user: Dict):
    """Create doctor profile after OTP verification"""
    
    # Generate unique employee ID
    employee_id = generate_employee_id()
    while db.query(DoctorDetails).filter(DoctorDetails.employee_id == employee_id).first():
        employee_id = generate_employee_id()
    
    # Check if email already exists
    existing_email = db.query(DoctorDetails).filter(
        DoctorDetails.email == doctor_data.email
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if license number already exists
    existing_license = db.query(DoctorDetails).filter(
        DoctorDetails.license_number == doctor_data.license_number
    ).first()
    if existing_license:
        raise HTTPException(status_code=400, detail="License number already registered")
    
    # Create full name
    full_name = f"{doctor_data.title} {doctor_data.first_name} {doctor_data.last_name}".strip()
    
    # Create doctor details
    doctor = DoctorDetails(
        employee_id=employee_id,
        title=doctor_data.title,
        first_name=doctor_data.first_name,
        last_name=doctor_data.last_name,
        full_name=full_name,
        specialization=doctor_data.specialization,
        email=doctor_data.email,
        phone=doctor_data.phone,
        phone_verified=True,
        department=doctor_data.department,
        qualification=doctor_data.qualification,
        experience_years=doctor_data.experience_years,
        license_number=doctor_data.license_number,
        status="pending",
        created_by=admin_user.get("user_id")
    )
    
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    
    # Create user account (pending approval)
    temp_password = generate_temp_password()
    
    user = User(
        username=employee_id,
        password=temp_password,
        role="doctor",
        is_approved=False,
        full_name=full_name,
        phone=doctor_data.phone,
        email=doctor_data.email
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Link user_id to doctor details
    doctor.user_id = user.id
    db.commit()
    
    return {
        "message": "Doctor profile created successfully. Pending admin approval.",
        "employee_id": employee_id,
        "doctor_id": doctor.id,
        "user_id": user.id,
        "temporary_password": temp_password,
        "phone": doctor_data.phone
    }

def get_all_doctors(db: Session, status: Optional[str] = None):
    """Get all doctors with optional status filter"""
    query = db.query(DoctorDetails)
    
    if status:
        query = query.filter(DoctorDetails.status == status)
    
    return query.order_by(DoctorDetails.created_at.desc()).all()

def get_pending_doctors(db: Session):
    """Get all pending doctors (for admin approval)"""
    doctors = db.query(DoctorDetails).filter(
        DoctorDetails.status == "pending"
    ).order_by(DoctorDetails.created_at.desc()).all()
    
    # Also get from User table for backward compatibility
    pending_users = db.query(User).filter(
        User.role == "doctor",
        User.is_approved == False
    ).all()
    
    # Combine and deduplicate
    result = []
    seen_ids = set()
    
    for d in doctors:
        result.append({
            "id": d.id,
            "user_id": d.user_id,
            "employee_id": d.employee_id,
            "full_name": d.full_name,
            "specialization": d.specialization,
            "email": d.email,
            "phone": d.phone,
            "phone_verified": d.phone_verified,
            "department": d.department,
            "qualification": d.qualification,
            "experience_years": d.experience_years,
            "license_number": d.license_number,
            "status": d.status,
            "created_at": d.created_at,
            "joining_date": d.joining_date
        })
        seen_ids.add(d.employee_id)
    
    for u in pending_users:
        if u.username not in seen_ids:
            result.append({
                "id": None,
                "user_id": u.id,
                "employee_id": u.username,
                "full_name": u.full_name,
                "specialization": "Not Specified",
                "email": u.email,
                "phone": u.phone,
                "phone_verified": False,
                "department": "Not Specified",
                "qualification": "Not Specified",
                "experience_years": 0,
                "license_number": "Not Specified",
                "status": "pending",
                "created_at": u.created_at,
                "joining_date": u.created_at
            })
    
    return result

def get_active_doctors(db: Session):
    """Get all approved/active doctors"""
    doctors = db.query(DoctorDetails).filter(
        DoctorDetails.status == "active"
    ).order_by(DoctorDetails.full_name).all()
    
    result = []
    for d in doctors:
        result.append({
            "id": d.id,
            "user_id": d.user_id,
            "employee_id": d.employee_id,
            "full_name": d.full_name,
            "specialization": d.specialization,
            "email": d.email,
            "phone": d.phone,
            "department": d.department,
            "qualification": d.qualification,
            "experience_years": d.experience_years,
            "license_number": d.license_number,
            "joining_date": d.joining_date,
            "approved_at": d.approved_at
        })
    
    return result

def get_doctor_by_id(db: Session, doctor_id: int):
    """Get doctor details by ID"""
    doctor = db.query(DoctorDetails).filter(
        DoctorDetails.id == doctor_id
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return doctor

def get_doctor_by_employee_id(db: Session, employee_id: str):
    """Get doctor details by employee ID"""
    doctor = db.query(DoctorDetails).filter(
        DoctorDetails.employee_id == employee_id
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return doctor

def approve_doctor(db: Session, doctor_id: int, admin_user: Dict):
    """Approve doctor and activate account"""
    # Try to find in DoctorDetails first
    doctor = db.query(DoctorDetails).filter(
        DoctorDetails.id == doctor_id
    ).first()
    
    if doctor:
        doctor.status = "active"
        doctor.approved_at = datetime.utcnow()
        doctor.approved_by = admin_user.get("user_id")
        
        # Update linked user account
        if doctor.user_id:
            user = db.query(User).filter(User.id == doctor.user_id).first()
            if user:
                user.is_approved = True
        
        db.commit()
        db.refresh(doctor)
        
        return {
            "message": f"Doctor {doctor.full_name} approved successfully",
            "doctor_id": doctor.id,
            "employee_id": doctor.employee_id,
            "status": doctor.status
        }
    
    # Fallback to User table
    user = db.query(User).filter(
        User.id == doctor_id,
        User.role == "doctor"
    ).first()
    
    if user:
        user.is_approved = True
        db.commit()
        
        return {
            "message": f"Doctor {user.full_name} approved successfully",
            "user_id": user.id,
            "username": user.username
        }
    
    raise HTTPException(status_code=404, detail="Doctor not found")

def reject_doctor(db: Session, doctor_id: int, admin_user: Dict):
    """Reject doctor application"""
    doctor = db.query(DoctorDetails).filter(
        DoctorDetails.id == doctor_id
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    doctor.status = "rejected"
    doctor.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": f"Doctor {doctor.full_name} rejected",
        "doctor_id": doctor.id
    }

def update_doctor_details(db: Session, doctor_id: int, update_data: Dict, admin_user: Dict):
    """Update doctor details"""
    doctor = db.query(DoctorDetails).filter(
        DoctorDetails.id == doctor_id
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    for key, value in update_data.items():
        if hasattr(doctor, key) and value is not None:
            setattr(doctor, key, value)
    
    # Update full name if first/last name changed
    if 'first_name' in update_data or 'last_name' in update_data or 'title' in update_data:
        title = update_data.get('title', doctor.title)
        first_name = update_data.get('first_name', doctor.first_name)
        last_name = update_data.get('last_name', doctor.last_name)
        doctor.full_name = f"{title} {first_name} {last_name}".strip()
    
    db.commit()
    db.refresh(doctor)
    
    return {"message": "Doctor details updated successfully", "doctor": doctor}

def delete_doctor(db: Session, doctor_id: int, admin_user: Dict):
    """Delete doctor (soft delete)"""
    doctor = db.query(DoctorDetails).filter(
        DoctorDetails.id == doctor_id
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    doctor.status = "inactive"
    db.commit()
    
    return {"message": f"Doctor {doctor.full_name} removed successfully"}

# ============ AUTH SERVICES ============

def login_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user.role == "doctor" and not user.is_approved:
        raise HTTPException(status_code=403, detail="Doctor not approved yet")
    
    token = create_access_token({
        "sub": user.username,
        "role": user.role,
        "user_id": user.id
    })
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return token, user.role

def register_doctor(db: Session, username: str, password: str, full_name: str):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    doctor = User(
        username=username,
        password=password,
        role="doctor",
        is_approved=False,
        full_name=full_name
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return {
        "message": "Doctor registered successfully. Waiting for admin approval.",
        "doctor_id": doctor.id
    }

# ============ PATIENT SERVICES ============

def create_patient(db: Session, patient_data):
    patient = Patient(
        name=patient_data.name,
        age=patient_data.age,
        blood_group=patient_data.blood_group,
        diagnosis=patient_data.diagnosis,
        treatment=patient_data.treatment
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return {
        "message": "Patient created successfully",
        "patient_id": patient.id
    }

def get_patient_by_id(db: Session, patient_id: int):
    return db.query(Patient).filter(Patient.id == patient_id).first()

def get_all_patients(db: Session):
    patients = db.query(Patient).all()
    
    result = []
    for p in patients:
        summary = db.query(DischargeSummary).filter(
            DischargeSummary.patient_id == p.id
        ).order_by(DischargeSummary.created_at.desc()).first()
        
        result.append({
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "blood_group": p.blood_group,
            "diagnosis": p.diagnosis,
            "treatment": p.treatment,
            "admission_date": p.admission_date,
            "discharge_date": p.discharge_date,
            "discharge_status": "Discharged" if summary and summary.approved else "Active",
            "summary_approved": summary.approved if summary else False
        })
    return result

def update_patient(db: Session, patient_id: int, patient_data):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return None
    
    if patient_data.name is not None:
        patient.name = patient_data.name
    if patient_data.age is not None:
        patient.age = patient_data.age
    if patient_data.blood_group is not None:
        patient.blood_group = patient_data.blood_group
    if patient_data.diagnosis is not None:
        patient.diagnosis = patient_data.diagnosis
    if patient_data.treatment is not None:
        patient.treatment = patient_data.treatment
    
    db.commit()
    db.refresh(patient)
    return patient

def delete_patient(db: Session, patient_id: int):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return None
    
    db.query(DischargeSummary).filter(DischargeSummary.patient_id == patient_id).delete()
    db.delete(patient)
    db.commit()
    return True

# ============ TEMPLATE SERVICES ============

def add_document(db: Session, filename: str, content: str):
    existing = db.query(ClinicalDocument).filter(ClinicalDocument.filename == filename).first()
    if existing:
        return {
            "message": "Template already exists",
            "template_id": existing.id
        }
    
    doc = ClinicalDocument(filename=filename, content=content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_all_documents(db: Session):
    return db.query(ClinicalDocument).all()

def get_document_by_id(db: Session, template_id: int):
    return db.query(ClinicalDocument).filter(ClinicalDocument.id == template_id).first()

def update_document(db: Session, template_id: int, filename: str, content: str):
    doc = db.query(ClinicalDocument).filter(ClinicalDocument.id == template_id).first()
    if not doc:
        return None
    doc.filename = filename
    doc.content = content
    db.commit()
    db.refresh(doc)
    return doc

def delete_document(db: Session, template_id: int):
    doc = db.query(ClinicalDocument).filter(ClinicalDocument.id == template_id).first()
    if not doc:
        return None
    db.delete(doc)
    db.commit()
    return True

# ============ DISCHARGE SUMMARY SERVICES ============

def generate_discharge(db: Session, patient_id: int):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return None
    
    existing = db.query(DischargeSummary).filter(
        DischargeSummary.patient_id == patient_id,
        DischargeSummary.approved == False
    ).first()
    
    if existing:
        return {
            "message": "Pending discharge summary already exists",
            "summary_id": existing.id,
            "summary": existing.summary
        }
    
    query = f"""
    Generate discharge summary for:
    Name: {patient.name}
    Age: {patient.age}
    Blood Group: {patient.blood_group}
    Diagnosis: {patient.diagnosis}
    Treatment: {patient.treatment}
    """
    
    summary_text = rag_pipeline(query, db)
    
    record = DischargeSummary(
        patient_id=patient.id,
        summary=summary_text,
        approved=False
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_discharge_summary_by_id(db: Session, summary_id: int):
    return db.query(DischargeSummary).filter(DischargeSummary.id == summary_id).first()

def get_pending_discharges(db: Session):
    pending = db.query(DischargeSummary).filter(
        DischargeSummary.approved == False
    ).order_by(DischargeSummary.created_at.desc()).all()
    
    result = []
    for p in pending:
        patient = db.query(Patient).filter(Patient.id == p.patient_id).first()
        result.append({
            "summary_id": p.id,
            "patient_id": p.patient_id,
            "patient_name": patient.name if patient else "Unknown",
            "summary": p.summary[:300] + "..." if len(p.summary) > 300 else p.summary,
            "generated_at": p.created_at
        })
    return result

def approve_discharge(db: Session, summary_id: int, approval):
    summary = db.query(DischargeSummary).filter(DischargeSummary.id == summary_id).first()
    if not summary:
        return None
    
    summary.approved = True
    summary.doctor_name = approval.doctor_name
    summary.doctor_signature = approval.doctor_signature
    summary.approved_at = datetime.utcnow()
    
    patient = db.query(Patient).filter(Patient.id == summary.patient_id).first()
    if patient:
        patient.discharge_date = datetime.utcnow()
    
    db.commit()
    db.refresh(summary)
    return summary

# ============ DASHBOARD SERVICES ============

def get_dashboard_stats(db: Session, user_role: str):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    stats = {
        "total_patients": db.query(Patient).count(),
        "generated_today": db.query(Patient).filter(Patient.created_at >= today_start).count()
    }
    
    if user_role == "admin":
        stats["pending_doctors"] = db.query(DoctorDetails).filter(
            DoctorDetails.status == "pending"
        ).count() + db.query(User).filter(
            User.role == "doctor", 
            User.is_approved == False
        ).count()
        
        stats["total_templates"] = db.query(ClinicalDocument).count()
        stats["pending_discharges"] = db.query(DischargeSummary).filter(
            DischargeSummary.approved == False
        ).count()
        stats["active_doctors"] = db.query(DoctorDetails).filter(
            DoctorDetails.status == "active"
        ).count()
    
    if user_role == "doctor":
        stats["pending_approvals"] = db.query(DischargeSummary).filter(
            DischargeSummary.approved == False
        ).count()
    
    return stats