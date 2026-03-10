from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from database.db import get_db
from models.schema import (
    LoginRequest, LoginResponse, DoctorRegister,
    PatientCreate, PatientUpdate, PatientResponse,
    ClinicalDocumentCreate, ClinicalDocumentResponse,
    DoctorApproval,
    RAGQuery, RAGResponse,
    DashboardStats,
    DoctorCreateRequest, DoctorCreateResponse,
    OTPRequest, OTPVerifyRequest, OTPVerifyResponse,
    DoctorResponse, DoctorApproveRequest
)
from services.rag import rag_pipeline
from services.service import (
    # Auth
    login_user, register_doctor,
    # Patient
    create_patient, get_all_patients, get_patient_by_id,
    update_patient, delete_patient,
    # Template
    add_document, get_all_documents, get_document_by_id,
    update_document, delete_document,
    # Discharge
    generate_discharge, get_discharge_summary_by_id,
    get_pending_discharges, approve_discharge,
    # Dashboard
    get_dashboard_stats,
    # OTP & Doctor Management - ALL FROM SERVICE.PY
    send_verification_otp, verify_phone_otp,
    create_doctor_profile, get_all_doctors,
    get_pending_doctors, get_active_doctors,
    get_doctor_by_id, get_doctor_by_employee_id,
    approve_doctor, reject_doctor,
    update_doctor_details, delete_doctor
)
from auth.auth import (
    require_auth, require_admin, require_doctor, get_current_user
)
from models.table_schema import Patient
from datetime import datetime

router = APIRouter(tags=["Clinical RAG"])

# ============ HEALTH ============

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Clinical Workflow API"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============ AUTH ============

@router.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token, role = login_user(db, payload.username, payload.password)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": role,
        "username": payload.username
    }

@router.post("/auth/register/doctor")
def register(payload: DoctorRegister, db: Session = Depends(get_db)):
    return register_doctor(db, payload.username, payload.password, payload.full_name)

@router.get("/auth/me")
def get_me(current_user: dict = Depends(require_auth)):
    return current_user

# ============ DOCTOR MANAGEMENT WITH OTP ============

@router.post("/doctor/otp/send")
def send_otp(payload: OTPRequest, db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    """Send OTP for phone verification"""
    return send_verification_otp(db, payload.phone)

@router.post("/doctor/otp/verify", response_model=OTPVerifyResponse)
def verify_otp(payload: OTPVerifyRequest, db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    """Verify OTP"""
    return verify_phone_otp(db, payload.phone, payload.otp)

@router.post("/doctor/create", response_model=DoctorCreateResponse)
def create_doctor(
    payload: DoctorCreateRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Create new doctor profile (after OTP verification)"""
    return create_doctor_profile(db, payload, admin)

@router.get("/doctors", response_model=List[DoctorResponse])
def get_doctors(
    status: Optional[str] = Query(None, enum=["pending", "active", "inactive", "all"]),
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Get all doctors (admin only)"""
    if status == "all" or not status:
        doctors = get_all_doctors(db)
    else:
        doctors = get_all_doctors(db, status)
    return doctors

@router.get("/doctors/pending")
def get_pending_doctors_list(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Get all pending doctors"""
    return get_pending_doctors(db)

@router.get("/doctors/active")
def get_active_doctors_list(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Get all active doctors"""
    return get_active_doctors(db)

@router.get("/doctors/{doctor_id}")
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Get doctor by ID"""
    return get_doctor_by_id(db, doctor_id)

@router.get("/doctors/employee/{employee_id}")
def get_doctor_by_emp_id(
    employee_id: str,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Get doctor by employee ID"""
    return get_doctor_by_employee_id(db, employee_id)

@router.post("/doctors/{doctor_id}/approve")
def approve_doctor_account(
    doctor_id: int,
    payload: Optional[DoctorApproveRequest] = None,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Approve doctor account"""
    return approve_doctor(db, doctor_id, admin)

@router.post("/doctors/{doctor_id}/reject")
def reject_doctor_account(
    doctor_id: int,
    payload: Optional[DoctorApproveRequest] = None,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Reject doctor application"""
    return reject_doctor(db, doctor_id, admin)

@router.put("/doctors/{doctor_id}")
def update_doctor_info(
    doctor_id: int,
    payload: DoctorCreateRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Update doctor details"""
    return update_doctor_details(db, doctor_id, payload.dict(), admin)

@router.delete("/doctors/{doctor_id}")
def delete_doctor_account(
    doctor_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Delete doctor account"""
    return delete_doctor(db, doctor_id, admin)

# ============ LEGACY ADMIN ROUTES ============

@router.get("/admin/pending-doctors")
def pending_doctors_legacy(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Get all doctors pending approval (legacy)"""
    return get_pending_doctors(db)

@router.post("/admin/approve-doctor/{doctor_id}")
def approve_doctor_account_legacy(
    doctor_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Approve doctor account (legacy)"""
    return approve_doctor(db, doctor_id, admin)

# ============ PATIENTS ============

@router.post("/patients")
def add_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    return create_patient(db, patient)

@router.get("/patients", response_model=List[PatientResponse])
def fetch_all_patients(
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    return get_all_patients(db)

@router.get("/patients/{patient_id}", response_model=PatientResponse)
def fetch_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        return {"detail": "Patient not found"}
    return patient

@router.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient_details(
    patient_id: int,
    patient: PatientUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    updated_patient = update_patient(db, patient_id, patient)
    if not updated_patient:
        return {"error": "Patient not found"}
    return updated_patient

@router.delete("/patients/{patient_id}")
def delete_patient_details(
    patient_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    result = delete_patient(db, patient_id)
    if not result:
        return {"error": "Patient not found"}
    return {"message": "Patient deleted successfully"}

# ============ TEMPLATES ============

@router.post("/templates")
def upload_document(
    payload: ClinicalDocumentCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    return add_document(db, payload.filename, payload.content)

@router.get("/templates")
def list_documents(
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    return get_all_documents(db)

@router.get("/templates/{template_id}")
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    doc = get_document_by_id(db, template_id)
    if not doc:
        return {"detail": "Template not found"}
    return doc

@router.put("/templates/{template_id}")
def update_template(
    template_id: int,
    payload: ClinicalDocumentCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    updated = update_document(db, template_id, payload.filename, payload.content)
    if not updated:
        return {"detail": "Template not found"}
    return {
        "message": "Template updated successfully",
        "template_id": updated.id
    }

@router.delete("/templates/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    result = delete_document(db, template_id)
    if not result:
        return {"detail": "Template not found"}
    return {"message": "Template deleted successfully"}

# ============ DISCHARGE SUMMARIES ============

@router.post("/discharge/generate/{patient_id}")
def generate_discharge_summary(
    patient_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    record = generate_discharge(db, patient_id)
    if not record:
        return {"detail": "Patient not found"}
    
    if "message" in record:
        return record
    
    return {
        "message": "Discharge summary generated",
        "summary_id": record.id,
        "patient_id": record.patient_id,
        "summary": record.summary,
        "approved": record.approved
    }

@router.get("/discharge/pending")
def get_pending_approvals(
    db: Session = Depends(get_db),
    doctor: dict = Depends(require_doctor)
):
    pending = get_pending_discharges(db)
    return pending

@router.post("/discharge/approve/{summary_id}")
def approve_summary(
    summary_id: int,
    approval: DoctorApproval,
    db: Session = Depends(get_db),
    doctor: dict = Depends(require_doctor)
):
    record = approve_discharge(db, summary_id, approval)
    if not record:
        return {"detail": "Discharge summary not found"}
    return {
        "message": "Discharge summary approved",
        "summary_id": record.id,
        "patient_id": record.patient_id,
        "approved": record.approved,
        "doctor_name": record.doctor_name,
        "approved_at": datetime.now().isoformat()
    }

@router.get("/discharge/{summary_id}")
def fetch_discharge_summary(
    summary_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    summary = get_discharge_summary_by_id(db, summary_id)
    if not summary:
        return {"detail": "Discharge summary not found"}
    
    patient = db.query(Patient).filter(Patient.id == summary.patient_id).first()
    
    return {
        "summary_id": summary.id,
        "patient_id": summary.patient_id,
        "patient_name": patient.name if patient else "Unknown",
        "summary": summary.summary,
        "approved": summary.approved,
        "doctor_name": summary.doctor_name,
        "approved_at": summary.approved_at
    }

# ============ DASHBOARD ============

@router.get("/dashboard/stats", response_model=DashboardStats)
def get_stats(
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    return get_dashboard_stats(db, user.get("role"))

# ============ RAG ============

@router.post("/generate", response_model=RAGResponse)
def generate_summary(
    payload: RAGQuery,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    answer = rag_pipeline(payload.query, db)
    return {"answer": answer}