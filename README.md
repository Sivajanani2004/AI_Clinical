# 🏥 AI Clinical Workflow System

A **professional clinical workflow dashboard** built using **Streamlit + FastAPI + AI (RAG)** with **Docker support**.  
This system helps hospitals manage patients, staff, discharge summaries, and provides an AI-powered clinical assistant.

---

## 📌 Project Overview

The **AI Clinical Workflow System** is a modern healthcare web application designed for:

- 👨‍⚕️ Doctors  
- 🧑‍💼 Hospital Admin Staff  

It simplifies:

- Patient management  
- Staff approval workflows  
- AI-based discharge summary generation  
- Clinical knowledge assistance  

---

## 🚀 Features

### 🔐 Authentication
- Secure login system  
- Token-based authentication  
- Role-based access (Admin / Doctor)  
- Session handling  

---

### 📊 Dashboard
- Overview statistics  
- Patient counts  
- Staff summary  
- Recent activity tracking  

---

### 🧑‍⚕️ Patient Management
- Add new patients  
- View patient records  
- Search & filter functionality  
- Dynamic patient table  

---

### 👩‍⚕️ Staff Management
- Admin can create doctor accounts  
- Doctor approval workflow  
- Pending & Active staff tabs  
- Role-based UI rendering  

---

### 📄 Clinical Templates
- Create discharge templates  
- Preview templates  
- Delete templates  
- Used for AI-based discharge generation  

---

### 🤖 AI Discharge Summary Generator
- Generates structured discharge summaries  
- Uses AI backend integration  
- Download summary as `.txt` file  

---

### 🧠 Clinical Assistant (RAG-based)
- AI-powered knowledge assistant  
- Provides clinical suggestions  
- Uses hospital data context  

---

## 🛠 Tech Stack

| Layer | Technology |
|------|-------------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Database | SQLite / SQLAlchemy |
| AI Layer | RAG / LLM Integration |
| Auth | Token-based authentication |
| Containerization | Docker |

---

## 📂 Project Structure

```bash
AI_Clinical/
│
├── backend/
│   ├── main.py
│   ├── models/
│   ├── services/
│   ├── auth/
│   └── Dockerfile
│
├── frontend/
│   ├── app1.py
│   └── Dockerfile
│
├── docker-compose.yml
├── requirements.txt
└── README.md
## ⚙️ Installation Guide

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Sivajanani2004/AI_Clinical.git
cd AI_Clinical
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

#### Activate Environment

**Windows**
```bash
venv\Scripts\activate
```

**Mac / Linux**
```bash
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---
### 4️⃣ Run Backend Server

```bash
uvicorn backend.main:app --reload
```

Backend will run at:
```bash
http://localhost:8000
```

API documentation:
```bash
http://localhost:8000/docs
```

### 5️⃣ Run Frontend Application

```bash
streamlit run frontend/app.py
```

Frontend dashboard:
```bash
http://localhost:8501
```
---

### 🐳 Run Using Docker

Build and Start Containers:
```bash
docker compose up --build
```

Stop Containers:

```bash
docker compose down
```
---

## 🔐 Default Roles

| Role   | Access |
|--------|--------|
| Admin  | Full system access |
| Doctor | Patient & discharge access |

---

## 📥 Discharge Summary Download

Generated summaries can be downloaded as:

```bash
discharge_summary.txt
```

---

## 🌍 Future Improvements

- JWT Authentication enhancement
- Cloud deployment (AWS / Azure)
- PDF export for discharge summary
- Audit logging
- Multi-hospital support

---

## 👩‍💻 Author

**Siva janani R**

---

## 📜 License

This project is for educational and demonstration purposes.
