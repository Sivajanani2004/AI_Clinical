import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import time
import random
import string

# ----------------------------------
# CONFIGURATION
# ----------------------------------
BASE_URL = "http://127.0.0.1:8000" 
st.set_page_config(
    page_title="Hospital Clinical Workflow System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------
# SESSION STATE INITIALIZATION
# ----------------------------------
if 'token' not in st.session_state:
    st.session_state.token = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'full_name' not in st.session_state:
    st.session_state.full_name = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'login_error' not in st.session_state:
    st.session_state.login_error = None
if 'employee_list' not in st.session_state:
    st.session_state.employee_list = []

# ----------------------------------
# HELPER FUNCTIONS
# ----------------------------------
def get_headers():
    """Get headers with auth token"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def make_request(method, endpoint, **kwargs):
    """Make authenticated request to backend"""
    headers = get_headers()
    if 'headers' in kwargs:
        headers.update(kwargs.pop('headers'))
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            timeout=10,
            **kwargs
        )
        return response
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to Hospital Server. Please contact IT Department.")
        return None
    except Exception as e:
        st.error(f"❌ System Error: {str(e)}")
        return None

def login(username, password):
    """Authenticate hospital staff"""
    response = make_request("POST", "/auth/login", json={
        "username": username,
        "password": password
    })
    
    if response and response.status_code == 200:
        data = response.json()
        st.session_state.token = data["access_token"]
        st.session_state.role = data["role"]
        st.session_state.username = data["username"]
        st.session_state.full_name = data.get("full_name", username)
        st.session_state.authenticated = True
        st.session_state.login_error = None
        return True, data["role"]
    elif response and response.status_code == 403:
        st.session_state.login_error = "pending"
        return False, "pending"
    else:
        st.session_state.login_error = "invalid"
        return False, None

def logout():
    """Secure logout"""
    st.session_state.token = None
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.full_name = None
    st.session_state.authenticated = False
    st.session_state.login_error = None
    st.rerun()

def generate_employee_id():
    """Generate unique employee ID"""
    year = datetime.now().strftime("%y")
    random_num = ''.join(random.choices(string.digits, k=4))
    return f"H{year}{random_num}"

def show_api_error(response, message="System Error"):
    """Display standardized error messages"""
    if response is None:
        st.error("❌ Cannot connect to Hospital Server")
    elif response.status_code == 401:
        st.error("🔒 Session expired. Please login again.")
        logout()
    elif response.status_code == 403:
        st.error("🚫 Access Denied - Insufficient privileges")
    else:
        try:
            error_detail = response.json().get("detail", "Unknown error")
            st.error(f"**{message}**\n{error_detail}")
        except:
            st.error(f"**{message}** (Error Code: {response.status_code})")

# ----------------------------------
# PROFESSIONAL HOSPITAL CSS
# ----------------------------------
st.markdown("""
<style>
    /* Import Medical Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hospital Professional Theme */
    .main-header {
        font-size: 2.2rem;
        color: #0b3d5f;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 600;
        border-bottom: 3px solid #2a7f6e;
        padding-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.6rem;
        color: #1e5668;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    .section-header {
        font-size: 1.3rem;
        color: #2a7f6e;
        margin-top: 1rem;
        margin-bottom: 1rem;
        font-weight: 500;
        border-left: 4px solid #2a7f6e;
        padding-left: 10px;
    }
    
    /* Professional Login Page */
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        padding: 2rem;
        border-radius: 0;
    }
    
    .login-container {
        width: 100%;
        max-width: 520px;
        margin: 0 auto;
        background: white;
        border-radius: 24px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .login-header {
        background: linear-gradient(135deg, #0b3d5f 0%, #1a5a7a 100%);
        padding: 2.5rem 2rem;
        text-align: center;
        border-bottom: 4px solid #2a7f6e;
    }
    
    .hospital-icon {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
    }
    
    .hospital-name {
        color: white;
        font-size: 1.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin: 0.5rem 0 0.25rem;
    }
    
    .hospital-tagline {
        color: rgba(255,255,255,0.9);
        font-size: 0.9rem;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    .login-body {
        padding: 2.5rem 2.5rem;
        background: white;
    }
    
    .welcome-text {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .welcome-title {
        color: #0b3d5f;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    .welcome-subtitle {
        color: #6b7280;
        font-size: 0.9rem;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 1.5px solid #e2e8f0 !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.2s !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2a7f6e !important;
        box-shadow: 0 0 0 3px rgba(42, 127, 110, 0.1) !important;
    }
    
    .stTextInput > div > div > input:hover {
        border-color: #cbd5e0 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2a7f6e 0%, #1e5f4a 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 6px rgba(42, 127, 110, 0.2) !important;
        margin-top: 1rem !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1e5f4a 0%, #154c3b 100%) !important;
        box-shadow: 0 6px 8px rgba(42, 127, 110, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 2px 4px rgba(42, 127, 110, 0.2) !important;
    }
    
    /* Security badge */
    .security-badge {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 40px;
        padding: 0.75rem 1.5rem;
        text-align: center;
        margin: 1.5rem 0 0;
        border: 1px solid #e2e8f0;
    }
    
    .security-badge p {
        color: #475569;
        font-size: 0.85rem;
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .security-badge span {
        color: #2a7f6e;
        font-weight: 600;
    }
    
    /* Error messages */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* Sidebar Navigation */
    .stSidebar .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 2px;
        padding: 0 !important;
    }
    .stSidebar .stRadio label {
        display: flex;
        align-items: center;
        padding: 10px 15px !important;
        margin: 0 !important;
        border-radius: 6px;
        font-size: 0.95rem;
        font-weight: 500;
        color: #1e293b;
        transition: all 0.2s;
        white-space: nowrap;
    }
    .stSidebar .stRadio label:hover {
        background-color: #e6f3ff !important;
        color: #0b3d5f !important;
    }
    
    /* Cards */
    .card {
        background-color: #f9fbfd;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #2a7f6e;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .staff-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .patient-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 6px;
        margin: 8px 0;
        border: 1px solid #e2e8f0;
    }
    
    .employee-id {
        font-family: monospace;
        background-color: #f1f5f9;
        padding: 2px 6px;
        border-radius: 4px;
        color: #0b3d5f;
        font-weight: 600;
    }
    
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-success {
        background-color: #d4edda;
        color: #155724;
    }
    .badge-warning {
        background-color: #fff3cd;
        color: #856404;
    }
    .badge-info {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    .badge-admin {
        background-color: #cce5ff;
        color: #004085;
    }
    .footer {
        text-align: center;
        color: #6c757d;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# PROFESSIONAL HOSPITAL LOGIN PAGE
# ----------------------------------
if not st.session_state.authenticated:
    # Create a wrapper for full-height background
    st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Professional hospital login container
        st.markdown("""
        <div class='login-container'>
            <div class='login-header'>
                <div class='hospital-icon'>🏥</div>
                <div class='hospital-name'>CITY GENERAL HOSPITAL</div>
                <div class='hospital-tagline'>Excellence in Patient Care</div>
            </div>
            <div class='login-body'>
        """, unsafe_allow_html=True)
        
        # Welcome message
        st.markdown("""
        <div class='welcome-text'>
            <div class='welcome-title'>Clinical Workflow System</div>
            <div class='welcome-subtitle'>Secure employee portal</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display login error messages
        if st.session_state.login_error == "invalid":
            st.error("❌ Invalid Employee ID or Password")
        elif st.session_state.login_error == "pending":
            st.warning("⏳ Your account is pending administrator approval")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input(
                "Employee ID", 
                placeholder="e.g., H240123",
                help="Enter your 6-digit hospital employee ID"
            )
            password = st.text_input(
                "Password", 
                type="password", 
                placeholder="••••••••",
                help="Enter your secure password"
            )
            
            submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
            
            if submitted:
                if username and password:
                    success, role = login(username, password)
                    if success:
                        st.success(f"✅ Welcome back, {st.session_state.full_name}!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.warning("⚠️ Please enter both Employee ID and Password")
        
        # Security badge
        st.markdown("""
        <div class='security-badge'>
            <p>
                <span>🔒 HIPAA Compliant</span> • 
                <span>🔐 256-bit Encryption</span> • 
                <span>📋 Audit Log Active</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Close login body and container
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Close wrapper
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # ----------------------------------
    # SIDEBAR - Professional Hospital Navigation
    # ----------------------------------
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0;'>
            <div style='background-color: #0b3d5f; color: white; padding: 1.2rem; border-radius: 8px;'>
                <h3 style='margin: 0; color: white;'>🏥 HOSPITAL</h3>
                <p style='margin: 0; opacity: 0.9; font-size: 0.8rem;'>Clinical Workflow System</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # User Profile Card
        st.markdown(f"""
        <div style='background-color: #f0f7fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
            <p style='margin: 0; color: #0b3d5f; font-weight: 600;'>{st.session_state.full_name}</p>
            <p style='margin: 0; color: #2a7f6e; font-size: 0.8rem;'>Employee ID: {st.session_state.username}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Role Badge
        if st.session_state.role == "admin":
            st.markdown("<span class='badge badge-admin'>👑 HOSPITAL ADMINISTRATOR</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='badge badge-success'>👨‍⚕️ MEDICAL DOCTOR</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # NAVIGATION - Role Based
        menu_options = []
        
        if st.session_state.role == "admin":
            menu_options = [
                "📊 DASHBOARD",
                "👤 ADD PATIENT",
                "📋 PATIENT RECORDS",
                "📄 TEMPLATE MGMT",
                "🤖 GENERATE DISCHARGE",
                "👨‍⚕️ APPROVE DOCTORS",
                "👥 STAFF MANAGEMENT",
                "📥 VIEW & DOWNLOAD",
                "🧠 CLINICAL ASSISTANT"
            ]
        else:  # doctor
            menu_options = [
                "📊 DASHBOARD",
                "📋 PATIENT RECORDS",
                "📄 VIEW TEMPLATES",
                "✅ APPROVE DISCHARGES",
                "📥 VIEW & DOWNLOAD",
                "🧠 CLINICAL ASSISTANT"
            ]
        
        menu = st.radio(
            "Navigation",
            options=menu_options,
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # System Status
        st.markdown("### 🔧 SYSTEM STATUS")
        response = make_request("GET", "/health")
        if response and response.status_code == 200:
            st.success("✅ Hospital Server: Online")
            st.markdown(f"**Session:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        else:
            st.error("❌ Hospital Server: Offline")
        
        # Logout Button
        st.markdown("---")
        if st.button("🚪 SECURE LOGOUT", use_container_width=True):
            logout()

    # ----------------------------------
    # DASHBOARD
    # ----------------------------------
    if menu == "📊 DASHBOARD":
        st.markdown("<h1 class='main-header'>🏥 HOSPITAL CLINICAL DASHBOARD</h1>", unsafe_allow_html=True)
        
        # Hospital Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        response = make_request("GET", "/dashboard/stats")
        stats = response.json() if response and response.status_code == 200 else {}
        
        with col1:
            st.metric("Total Patients", stats.get("total_patients", 0))
        with col2:
            st.metric("Admitted Today", stats.get("generated_today", 0))
        
        if st.session_state.role == "admin":
            with col3:
                st.metric("Active Staff", stats.get("active_doctors", 0))
            with col4:
                st.metric("Pending Approvals", stats.get("pending_doctors", 0))
        else:
            with col3:
                st.metric("Pending Reviews", stats.get("pending_approvals", 0))
            with col4:
                st.metric("Active Patients", stats.get("total_patients", 0))
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h2 class='section-header'>📋 Recent Admissions</h2>", unsafe_allow_html=True)
            response = make_request("GET", "/patients")
            patients = response.json() if response and response.status_code == 200 else []
            
            if patients:
                for patient in patients[:5]:
                    st.markdown(f"""
                    <div class='patient-card'>
                        <div style='display: flex; justify-content: space-between;'>
                            <strong style='color: #0b3d5f;'>{patient['name']}</strong>
                            <span class='badge {"badge-success" if patient["discharge_status"] == "Discharged" else "badge-warning"}'>
                                {patient['discharge_status']}
                            </span>
                        </div>
                        <span style='color: #6c757d; font-size: 0.9rem;'>Age: {patient['age']} | MRN: {patient['id']}</span><br>
                        <span style='color: #6c757d; font-size: 0.85rem;'>Diagnosis: {patient['diagnosis'][:60]}...</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📭 No recent admissions")
        
        with col2:
            if st.session_state.role == "admin":
                st.markdown("<h2 class='section-header'>👨‍⚕️ Pending Staff Approvals</h2>", unsafe_allow_html=True)
                response = make_request("GET", "/admin/pending-doctors")
                pending = response.json() if response and response.status_code == 200 else []
                
                if pending:
                    for doctor in pending[:5]:
                        st.markdown(f"""
                        <div class='staff-card'>
                            <strong style='color: #0b3d5f;'>{doctor['full_name']}</strong><br>
                            <span style='color: #6c757d;'>Employee ID: <span class='employee-id'>{doctor['username']}</span></span><br>
                            <span style='color: #6c757d;'>Registered: {doctor['created_at'][:10]}</span><br>
                            <span class='badge badge-warning' style='margin-top: 5px;'>Pending Approval</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No pending staff approvals")
            else:
                st.markdown("<h2 class='section-header'>✅ Pending Discharge Approvals</h2>", unsafe_allow_html=True)
                response = make_request("GET", "/discharge/pending")
                pending = response.json() if response and response.status_code == 200 else []
                
                if pending:
                    for item in pending[:5]:
                        st.markdown(f"""
                        <div class='staff-card'>
                            <strong style='color: #0b3d5f;'>Patient: {item['patient_name']}</strong><br>
                            <span style='color: #6c757d;'>Summary ID: #{item['summary_id']}</span><br>
                            <span style='color: #6c757d;'>Generated: {item['generated_at'][:10]}</span><br>
                            <span class='badge badge-warning' style='margin-top: 5px;'>Awaiting Review</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No pending approvals")

    # ----------------------------------
    # ADD PATIENT (Admin Only)
    # ----------------------------------
    elif menu == "👤 ADD PATIENT" and st.session_state.role == "admin":
        st.markdown("<h1 class='sub-header'>👤 New Patient Registration</h1>", unsafe_allow_html=True)
        
        with st.form("patient_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name *", placeholder="Patient's legal name")
                age = st.number_input("Age *", min_value=0, max_value=120, value=45)
            with col2:
                blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
                admission_type = st.selectbox("Admission Type", ["Emergency", "Elective", "Urgent", "Scheduled"])
            
            diagnosis = st.text_area("Primary Diagnosis *", placeholder="ICD-10 code and description", height=80)
            treatment = st.text_area("Treatment Plan *", placeholder="Prescribed medications, procedures, and care plan", height=100)
            
            col3, col4 = st.columns(2)
            with col3:
                admitting_doctor = st.text_input("Admitting Physician", value=st.session_state.full_name, disabled=True)
            with col4:
                department = st.selectbox("Department", ["Cardiology", "Neurology", "Pediatrics", "Oncology", "Orthopedics", "Surgery", "Internal Medicine"])
            
            st.caption("* Required fields")
            
            submitted = st.form_submit_button("➕ REGISTER PATIENT", type="primary", use_container_width=True)
            
            if submitted:
                if not all([name, diagnosis, treatment]):
                    st.warning("⚠️ Please complete all required fields")
                else:
                    response = make_request("POST", "/patients", json={
                        "name": name.strip(),
                        "age": age,
                        "blood_group": blood_group,
                        "diagnosis": diagnosis.strip(),
                        "treatment": treatment.strip()
                    })
                    
                    if response and response.status_code == 200:
                        st.success(f"✅ Patient '{name}' registered successfully!")
                        st.balloons()

    # ----------------------------------
    # PATIENT RECORDS (Admin & Doctor)
    # ----------------------------------
    elif menu == "📋 PATIENT RECORDS":
        st.markdown("<h1 class='sub-header'>📋 Hospital Patient Records</h1>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search = st.text_input("🔍 Search patients", placeholder="Search by name, MRN, diagnosis, or doctor")
        with col2:
            filter_status = st.selectbox("Filter", ["All", "Active", "Discharged"])
        with col3:
            if st.button("🔄 REFRESH", use_container_width=True):
                st.rerun()
        
        response = make_request("GET", "/patients")
        patients = response.json() if response and response.status_code == 200 else []
        
        if patients:
            df = pd.DataFrame(patients)
            
            if search:
                mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
                df = df[mask]
            
            if filter_status == "Active":
                df = df[df['discharge_status'] != 'Discharged']
            elif filter_status == "Discharged":
                df = df[df['discharge_status'] == 'Discharged']
            
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "MRN",
                    "name": "Patient Name",
                    "age": "Age",
                    "diagnosis": "Diagnosis",
                    "discharge_status": "Status",
                    "admission_date": "Admitted"
                }
            )
            
            st.info(f"📊 Showing {len(df)} of {len(patients)} patient records")
        else:
            st.info("📭 No patient records found")

    # ----------------------------------
    # TEMPLATE MGMT (Admin Only)
    # ----------------------------------
    elif menu == "📄 TEMPLATE MGMT" and st.session_state.role == "admin":
        st.markdown("<h1 class='sub-header'>📄 Clinical Template Management</h1>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["➕ CREATE TEMPLATE", "📋 TEMPLATE LIBRARY"])
        
        with tab1:
            with st.form("add_template_form"):
                filename = st.text_input("Template Name", placeholder="e.g., cardiac_discharge_v1")
                template_type = st.selectbox("Template Type", ["Discharge Summary", "Prescription", "Referral Letter", "Lab Report"])
                content = st.text_area("Template Content", height=300, 
                    placeholder="Enter the clinical template content with placeholders...")
                
                if st.form_submit_button("💾 SAVE TO HOSPITAL DATABASE", type="primary", use_container_width=True):
                    if filename and content:
                        response = make_request("POST", "/templates", json={
                            "filename": filename,
                            "content": content
                        })
                        if response and response.status_code == 200:
                            st.success(f"✅ Template '{filename}' saved successfully")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.warning("⚠️ Template name and content required")
        
        with tab2:
            response = make_request("GET", "/templates")
            templates = response.json() if response and response.status_code == 200 else []
            
            if templates:
                for template in templates:
                    with st.expander(f"📄 {template['filename']}"):
                        st.text_area("Content", value=template['content'], height=200, disabled=True)
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✏️ EDIT", key=f"edit_{template['id']}"):
                                st.session_state[f"editing_{template['id']}"] = True
                        with col2:
                            if st.button("🗑️ DELETE", key=f"del_{template['id']}"):
                                del_resp = make_request("DELETE", f"/templates/{template['id']}")
                                if del_resp and del_resp.status_code == 200:
                                    st.success("Template removed")
                                    time.sleep(1)
                                    st.rerun()
            else:
                st.info("No templates in library")

    # ----------------------------------
    # VIEW TEMPLATES (Doctor Read Only)
    # ----------------------------------
    elif menu == "📄 VIEW TEMPLATES" and st.session_state.role == "doctor":
        st.markdown("<h1 class='sub-header'>📄 Clinical Reference Templates</h1>", unsafe_allow_html=True)
        
        response = make_request("GET", "/templates")
        templates = response.json() if response and response.status_code == 200 else []
        
        if templates:
            for template in templates:
                with st.expander(f"📄 {template['filename']}"):
                    st.text_area("Content", value=template['content'], height=200, disabled=True)
        else:
            st.info("No templates available")

    # ----------------------------------
    # GENERATE DISCHARGE (Admin Only)
    # ----------------------------------
    elif menu == "🤖 GENERATE DISCHARGE" and st.session_state.role == "admin":
        st.markdown("<h1 class='sub-header'>🤖 AI Discharge Summary Generator</h1>", unsafe_allow_html=True)
        
        response = make_request("GET", "/patients")
        patients = response.json() if response and response.status_code == 200 else []
        
        if patients:
            active_patients = [p for p in patients if p['discharge_status'] != 'Discharged']
            
            if active_patients:
                patient_options = {f"{p['id']} - {p['name']} (Age: {p['age']})": p['id'] for p in active_patients}
                selected = st.selectbox("Select Patient for Discharge", options=list(patient_options.keys()))
                patient_id = patient_options[selected]
                
                if st.button("🚀 GENERATE DISCHARGE SUMMARY", type="primary", use_container_width=True):
                    with st.spinner("AI analyzing patient records and clinical templates..."):
                        response = make_request("POST", f"/discharge/generate/{patient_id}")
                        
                        if response and response.status_code == 200:
                            data = response.json()
                            
                            st.markdown("### 📋 AI-Generated Discharge Summary")
                            
                            if "message" in data:
                                st.info(data["message"])
                            
                            summary = st.text_area(
                                "Discharge Summary",
                                value=data.get("summary", ""),
                                height=400,
                                key="generated_summary"
                            )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    "💾 DOWNLOAD TXT",
                                    data=summary,
                                    file_name=f"discharge_{patient_id}_{datetime.now().strftime('%Y%m%d')}.txt",
                                    use_container_width=True
                                )
                            with col2:
                                st.info(f"Status: {data.get('status', 'Pending Medical Review')}")
            else:
                st.warning("No active patients available for discharge")
        else:
            st.warning("No patients in system")

    # ----------------------------------
    # APPROVE DOCTORS (Admin Only)
    # ----------------------------------
    elif menu == "👨‍⚕️ APPROVE DOCTORS" and st.session_state.role == "admin":
        st.markdown("<h1 class='sub-header'>👨‍⚕️ Doctor Approval Queue</h1>", unsafe_allow_html=True)
        
        response = make_request("GET", "/admin/pending-doctors")
        pending = response.json() if response and response.status_code == 200 else []
        
        if pending:
            st.markdown(f"**Pending Approvals:** {len(pending)}")
            
            for doctor in pending:
                with st.container():
                    st.markdown(f"""
                    <div class='card'>
                        <h3 style='color: #0b3d5f;'>{doctor['full_name']}</h3>
                        <p><strong>Employee ID:</strong> <span class='employee-id'>{doctor['username']}</span></p>
                        <p><strong>Registration Date:</strong> {doctor['created_at'][:10]}</p>
                        <p><strong>Status:</strong> <span class='badge badge-warning'>Awaiting Approval</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ APPROVE", key=f"approve_{doctor['id']}", use_container_width=True):
                            approve_resp = make_request("POST", f"/admin/approve-doctor/{doctor['id']}")
                            if approve_resp and approve_resp.status_code == 200:
                                st.success(f"✅ Dr. {doctor['full_name']} approved!")
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                    with col2:
                        if st.button("❌ REJECT", key=f"reject_{doctor['id']}", use_container_width=True):
                            st.warning("Rejection functionality to be implemented")
                    st.markdown("---")
        else:
            st.info("✅ No pending doctor approvals")
            st.balloons()

    # ----------------------------------
    # STAFF MANAGEMENT (Admin Only)
    # ----------------------------------
    elif menu == "👥 STAFF MANAGEMENT" and st.session_state.role == "admin":
        st.markdown("<h1 class='sub-header'>👥 Hospital Staff Management</h1>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["➕ ADD NEW DOCTOR", "📋 ACTIVE STAFF", "⏳ PENDING APPROVALS"])
        
        with tab1:
            st.markdown("""
            <div style='background-color: #e6f3ff; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;'>
                <strong>🔐 CREATE NEW HOSPITAL STAFF ACCOUNT</strong><br>
                Fill in the details below to create a new doctor account. 
                The employee ID will be automatically generated.
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("create_staff_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    title = st.selectbox("Title", ["Dr.", "Prof.", "Mr.", "Ms.", "Mrs."])
                    first_name = st.text_input("First Name *")
                    last_name = st.text_input("Last Name *")
                    specialization = st.selectbox("Specialization", [
                        "Cardiology", "Neurology", "Pediatrics", "Oncology", 
                        "Orthopedics", "Radiology", "Surgery", "Internal Medicine",
                        "Emergency Medicine", "Psychiatry", "Dermatology", "Other"
                    ])
                
                with col2:
                    employee_id = generate_employee_id()
                    st.text_input("Employee ID (Auto-generated)", value=employee_id, disabled=True)
                    email = st.text_input("Email Address *")
                    phone = st.text_input("Contact Number")
                
                st.markdown("---")
                col3, col4 = st.columns(2)
                with col3:
                    temp_password = st.text_input("Temporary Password *", type="password", 
                                                placeholder="Min 8 characters")
                with col4:
                    confirm_password = st.text_input("Confirm Password *", type="password")
                
                st.caption("⚠️ Staff will be required to change password on first login")
                
                create_btn = st.form_submit_button("👤 CREATE DOCTOR ACCOUNT", type="primary", use_container_width=True)
                
                if create_btn:
                    full_name = f"{title} {first_name} {last_name}".strip()
                    
                    if not all([first_name, last_name, email, temp_password, confirm_password]):
                        st.warning("⚠️ Please fill all required fields")
                    elif temp_password != confirm_password:
                        st.error("❌ Passwords do not match")
                    elif len(temp_password) < 8:
                        st.warning("⚠️ Password must be at least 8 characters")
                    else:
                        response = make_request("POST", "/auth/register/doctor", json={
                            "username": employee_id,
                            "password": temp_password,
                            "full_name": full_name
                        })
                        
                        if response and response.status_code == 200:
                            st.success(f"✅ Doctor account created successfully!")
                            st.info(f"""
                            **Account Details:**
                            - **Employee ID:** `{employee_id}`
                            - **Full Name:** {full_name}
                            - **Specialization:** {specialization}
                            - **Status:** Pending Approval
                            
                            Please provide these credentials to the doctor.
                            """)
                            time.sleep(3)
                            st.rerun()
                        elif response and response.status_code == 400:
                            st.error("❌ Employee ID already exists. Please try again.")
                        else:
                            show_api_error(response, "Account creation failed")
        
        with tab2:
            st.markdown("### 🏥 Active Medical Staff")
            response = make_request("GET", "/doctors/active")
            active = response.json() if response and response.status_code == 200 else []
            
            if active:
                for doctor in active:
                    st.markdown(f"""
                    <div class='staff-card'>
                        <div style='display: flex; justify-content: space-between;'>
                            <strong style='color: #0b3d5f;'>{doctor['full_name']}</strong>
                            <span class='badge badge-success'>Active</span>
                        </div>
                        <span style='color: #6c757d;'>Employee ID: <span class='employee-id'>{doctor['employee_id']}</span></span><br>
                        <span style='color: #6c757d;'>Specialization: {doctor['specialization']}</span><br>
                        <span style='color: #6c757d;'>Department: {doctor['department']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No active staff members found")
        
        with tab3:
            st.markdown("### ⏳ Pending Staff Approvals")
            response = make_request("GET", "/admin/pending-doctors")
            pending = response.json() if response and response.status_code == 200 else []
            
            if pending:
                for doctor in pending:
                    with st.container():
                        st.markdown(f"""
                        <div class='card'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <h3 style='color: #0b3d5f; margin: 0;'>{doctor['full_name']}</h3>
                                    <p style='margin: 5px 0;'><strong>Employee ID:</strong> <span class='employee-id'>{doctor['username']}</span></p>
                                    <p style='margin: 5px 0;'><strong>Registration Date:</strong> {doctor['created_at'][:10]}</p>
                                </div>
                                <span class='badge badge-warning'>Pending</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("✅ APPROVE STAFF ACCESS", key=f"approve_{doctor['id']}", use_container_width=True):
                            approve_resp = make_request("POST", f"/admin/approve-doctor/{doctor['id']}")
                            if approve_resp and approve_resp.status_code == 200:
                                st.success(f"✅ Access granted for {doctor['full_name']}")
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
            else:
                st.info("No pending staff approvals")

    # ----------------------------------
    # APPROVE DISCHARGES (Doctor Only)
    # ----------------------------------
    elif menu == "✅ APPROVE DISCHARGES" and st.session_state.role == "doctor":
        st.markdown("<h1 class='sub-header'>✅ Discharge Summary Review</h1>", unsafe_allow_html=True)
        
        response = make_request("GET", "/discharge/pending")
        pending = response.json() if response and response.status_code == 200 else []
        
        if pending:
            for item in pending:
                with st.expander(f"Patient: {item['patient_name']} (Summary #{item['summary_id']})"):
                    st.markdown(f"**Generated:** {item['generated_at'][:16]}")
                    st.text_area("Summary Content", value=item['summary'], height=200, disabled=True)
                    
                    with st.form(f"approve_form_{item['summary_id']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            doctor_name = st.text_input("Attending Physician", 
                                                      value=st.session_state.full_name,
                                                      disabled=True)
                        with col2:
                            signature = st.text_input("Digital Signature / License #", 
                                                    placeholder="Enter your medical license number")
                        
                        approve_btn = st.form_submit_button("✅ APPROVE & FINALIZE", type="primary", use_container_width=True)
                        
                        if approve_btn:
                            if signature:
                                payload = {
                                    "doctor_name": st.session_state.full_name,
                                    "doctor_signature": signature
                                }
                                approve_resp = make_request("POST", f"/discharge/approve/{item['summary_id']}", json=payload)
                                
                                if approve_resp and approve_resp.status_code == 200:
                                    st.success("✅ Discharge summary approved and finalized")
                                    st.balloons()
                                    time.sleep(2)
                                    st.rerun()
                            else:
                                st.warning("⚠️ Digital signature required")
        else:
            st.info("No discharge summaries pending review")

    # ----------------------------------
    # VIEW & DOWNLOAD (All authenticated users)
    # ----------------------------------
    elif menu == "📥 VIEW & DOWNLOAD":
        st.markdown("<h1 class='sub-header'>📥 Discharge Summary Archive</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            summary_id = st.number_input("Enter Discharge Summary ID", min_value=1, step=1)
        with col2:
            if st.button("🔍 RETRIEVE", use_container_width=True):
                response = make_request("GET", f"/discharge/{summary_id}")
                
                if response and response.status_code == 200:
                    data = response.json()
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Patient", data.get('patient_name', 'N/A'))
                    with col2:
                        status = "✅ APPROVED" if data.get('approved') else "⏳ PENDING"
                        st.metric("Status", status)
                    with col3:
                        if data.get('doctor_name'):
                            st.metric("Approved By", data['doctor_name'])
                    
                    st.markdown("### 📄 Discharge Summary Document")
                    summary_text = st.text_area(
                        "Summary Content",
                        value=data.get('summary', ''),
                        height=400,
                        disabled=True
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "📥 DOWNLOAD TXT",
                            data=summary_text,
                            file_name=f"discharge_{summary_id}_{datetime.now().strftime('%Y%m%d')}.txt",
                            use_container_width=True
                        )
                    with col2:
                        st.download_button(
                            "📊 EXPORT JSON",
                            data=json.dumps(data, indent=2, default=str),
                            file_name=f"discharge_{summary_id}.json",
                            mime="application/json",
                            use_container_width=True
                        )

    # ----------------------------------
    # CLINICAL ASSISTANT (RAG)
    # ----------------------------------
    elif menu == "🧠 CLINICAL ASSISTANT":
        st.markdown("<h1 class='sub-header'>🧠 AI Clinical Decision Support</h1>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background-color: #e6f3ff; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
            <strong>🔬 HOSPITAL USE ONLY</strong><br>
            This AI assistant searches approved clinical templates and hospital protocols.
            All responses are for reference only and do not replace clinical judgment.
        </div>
        """, unsafe_allow_html=True)
        
        query = st.text_area(
            "Enter your clinical query",
            placeholder="e.g., What are the standard discharge criteria for post-operative cardiac patients?",
            height=100
        )
        
        if st.button("🚀 QUERY CLINICAL KNOWLEDGE BASE", type="primary", use_container_width=True):
            if query:
                with st.spinner("🔍 Searching hospital protocols and templates..."):
                    response = make_request("POST", "/generate", json={"query": query})
                    
                    if response and response.status_code == 200:
                        answer = response.json().get("answer", "")
                        
                        st.markdown("### 🤖 Clinical Assistant Response")
                        st.markdown(f"""
                        <div style='background-color: #f8fafc; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #2a7f6e;'>
                            {answer}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please enter a clinical query")

# ----------------------------------
# PROFESSIONAL HOSPITAL FOOTER
# ----------------------------------
st.markdown("---")
st.markdown("""
<div class='footer'>
    <p>© 2026 City General Hospital | Clinical Workflow System v2.0.0</p>
    <p style='font-size: 0.7rem; margin-top: 0.5rem;'>
        🏥 Accredited by Joint Commission International | HIPAA Compliant<br>
        All activities are logged and monitored for security
    </p>
</div>
""", unsafe_allow_html=True)