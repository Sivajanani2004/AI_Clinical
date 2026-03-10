from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ============ AUTH ============
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
    full_name: Optional[str] = None

class DoctorRegister(BaseModel):
    username: str
    password: str
    full_name: str

# ============ PATIENT ============
class PatientCreate(BaseModel):
    name: str
    age: int
    blood_group: str
    diagnosis: str
    treatment: str

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    blood_group: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None

class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    blood_group: str
    diagnosis: str
    treatment: str
    admission_date: datetime
    discharge_date: Optional[datetime] = None
    discharge_status: Optional[str] = None
    summary_approved: Optional[bool] = None
    class Config:
        from_attributes = True

# ============ TEMPLATE ============
class ClinicalDocumentCreate(BaseModel):
    filename: str
    content: str

class ClinicalDocumentResponse(BaseModel):
    id: int
    filename: str
    content: str
    created_at: datetime
    class Config:
        from_attributes = True

# ============ DISCHARGE ============
class DoctorApproval(BaseModel):
    doctor_name: str
    doctor_signature: str

# ============ RAG ============
class RAGQuery(BaseModel):
    query: str

class RAGResponse(BaseModel):
    answer: str

# ============ DASHBOARD ============
class DashboardStats(BaseModel):
    total_patients: int
    generated_today: int
    pending_doctors: Optional[int] = None
    total_templates: Optional[int] = None
    pending_discharges: Optional[int] = None
    pending_approvals: Optional[int] = None
    active_doctors: Optional[int] = None

# ============ DOCTOR MANAGEMENT ============
class DoctorCreateRequest(BaseModel):
    title: str
    first_name: str
    last_name: str
    specialization: str
    email: str
    phone: str
    department: str
    qualification: str
    experience_years: int
    license_number: str

class DoctorCreateResponse(BaseModel):
    message: str
    employee_id: str
    doctor_id: int
    user_id: int
    temporary_password: str
    phone: str

class OTPRequest(BaseModel):
    phone: str

class OTPVerifyRequest(BaseModel):
    phone: str
    otp: str

class OTPVerifyResponse(BaseModel):
    message: str
    verified: bool
    phone: str

class DoctorResponse(BaseModel):
    id: int
    user_id: Optional[int]
    employee_id: str
    title: str
    first_name: str
    last_name: str
    full_name: str
    specialization: str
    email: str
    phone: str
    phone_verified: bool
    department: str
    qualification: str
    experience_years: int
    license_number: str
    status: str
    joining_date: datetime
    created_at: datetime
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DoctorApproveRequest(BaseModel):
    comments: Optional[str] = None