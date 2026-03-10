# 🏥 AI Clinical Workflow System

A **professional clinical workflow dashboard** built using **Streamlit** with backend API integration.  
This system helps hospitals manage patients, staff, discharge summaries, and includes an AI-powered clinical assistant.

---

## 📌 Project Overview

The **AI Clinical Workflow System** is a modern web application designed for:

- 👨‍⚕️ Doctors  
- 🧑‍💼 Admin Staff  

It streamlines:

- Patient management  
- Staff approval workflow  
- Discharge summary generation  
- Clinical AI assistance  
- Secure authentication  

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

| Layer        | Technology |
|-------------|------------|
| Frontend    | Streamlit |
| Backend     | FastAPI |
| Database    | SQLite / SQLAlchemy |
| AI Layer    | RAG / LLM Integration |
| Auth        | Token-based authentication |

---

## 📂 Project Structure

```bash
AI_Clinical/
│
├── app.py
├── requirements.txt
├── backend/
│   ├── models.py
│   ├── routes.py
│   └── database.py
│
├── templates/
├── utils/
└── README.md
```

---

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

### 4️⃣ Run the Application

```bash
streamlit run app.py
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
