# 🏥 AI Clinical Workflow System

A **professional clinical workflow dashboard** for hospitals built with **Streamlit** and integrated with a backend API.  
This system provides a secure employee portal, patient management, staff management, discharge summary generation, and an AI-powered clinical assistant.

---

## 🚀 Project Overview

The **AI Clinical Workflow System** is a modern web application designed for hospital staff — doctors and administrators — to streamline clinical tasks and documentation.

It features:

✔ Secure login & role-based access  
✔ Patient registration and record management  
✔ Discharge summary generator (AI assisted)  
✔ Doctor approval & staff management  
✔ Discharge summary archive with export options  
✔ AI-driven clinical decision support (RAG-based)  
✔ Responsive and professional interface built using Streamlit  

---

## 📌 Features

### 🔐 Authentication
- Secure login using token-based authentication
- Role-based UI rendering
- Admin and Doctor roles

### 🏨 Dashboard
- Overview of patient stats
- Pending tasks and recent activity display

### 👤 Patient Records
- Add and manage patient information
- Search and filter records
- Dynamic table view

### 🧑‍⚕️ Staff Management
- Admin can create doctor accounts
- Doctors get approved by admin
- Multi-tab UI for active and pending staff

### 📄 Templates
- Create, preview, and delete clinical templates
- Used for AI-based discharge summary generation

### 🤖 AI Discharge Generator
- Generates clinical discharge summaries
- Download as TEXT files

### 🧠 Clinical Assistant
- AI-based searchable knowledge assistant
- Provides clinical answers with hospital data

---

## 📦 Tech Stack

| Component | Technology |
|-----------|-------------|
| Frontend | Streamlit |
| Backend | FastAPI (assumed) |
| AI Assistant | Integration with RAG / Chat API |
| Authentication | Token based |

---

## 🧠 Screenshot

<!-- Optional: You can place screenshots here to show UI -->

---

## 🛠 Installation

1. Clone the Repo:
```bash
git clone https://github.com/Sivajanani2004/AI_Clinical.git

2.Create and activate Python environment:

python -m venv venv
source venv/bin/activate      # Mac / Linux
venv\Scripts\activate         # Windows


3.Install requirements:

pip install -r requirements.txt


4.Run the app:

``bash

streamlit run app.py
