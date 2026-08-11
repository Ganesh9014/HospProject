# 🏥 Hospital Management System — Master Project Documentation

Welcome to the central documentation for the **Hospital Management System**. This document provides an all-in-one technical reference covering system architecture, workspace structure, database setup, environment configuration, production build pipeline, Windows deployment, live server update procedures, core clinical workflows, and web REST APIs.

---

## 📋 Table of Contents
1. [System Architecture & Overview](#1-system-architecture--overview)
2. [Technology Stack & Prerequisites](#2-technology-stack--prerequisites)
3. [Workspace Directory Structure](#3-workspace-directory-structure)
4. [Environment Configuration (`.env`)](#4-environment-configuration-env)
5. [Database Setup & Management](#5-database-setup--management)
6. [Production Build System](#6-production-build-system)
7. [Production Server Deployment & Autorun](#7-production-server-deployment--autorun)
8. [Live Server Update & Backup Procedures](#8-live-server-update--backup-procedures)
9. [Core Features & Web Workflows](#9-core-features--web-workflows)
10. [Web REST Integration Reference](#10-web-rest-integration-reference)

---

## 1. 📌 System Architecture & Overview

The **Hospital Management System** is an enterprise-grade web application engineered using Django, Waitress WSGI Server, WhiteNoise static asset handler, and Microsoft SQL Server.

### Key Architectural Highlights
- **Secure Code Packaging:** Pre-compiled Python bytecode (`.pyc`) deployment protects proprietary business logic and source code on hospital servers.
- **LAN Multi-Workstation Access:** Designed to run on a central hospital server and serve receptionists, doctors, nurses, lab technicians, and administrators across the local area network.
- **Robust Database Connectivity:** Built-in connection retry handlers ensure resilient server booting, managing SQL Server service startup delays smoothly.
- **Role-Based Access Control:** Dynamic menu and permissions system based on employee designations and assigned hospital roles.

```
       ┌────────────────────────────────────────────────────────┐
       │                 Hospital Client Browsers                │
       │    (Doctor Workstation, Reception, Lab, Pharmacy)      │
       └───────────────────────────┬────────────────────────────┘
                                   │ HTTP / LAN (Port 8000)
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                Waitress WSGI Web Server                │
       │                   (serve.py - 0.0.0.0)                 │
       └─────────────┬────────────────────────────┬─────────────┘
                     │                            │
                     ▼                            ▼
       ┌──────────────────────────┐   ┌──────────────────────────┐
       │     Django App Logic     │   │   WhiteNoise Middleware  │
       │  (hospApp compiled .pyc) │   │    (Static & Media)      │
       └─────────────┬────────────┘   └──────────────────────────┘
                     │
                     ▼
       ┌──────────────────────────┐
       │  Microsoft SQL Server    │
       │    (hospitalDatabase)    │
       └──────────────────────────┘
```

---

## 2. 🛠️ Technology Stack & Prerequisites

### Technology Stack
- **Web Framework:** Django (Python 3.10, 3.11, or 3.12)
- **WSGI Production Server:** `Waitress` (Production multi-threaded server for Windows)
- **Static & Media File Handler:** `WhiteNoise`
- **Database Engine:** Microsoft SQL Server (2019, 2022, or SQL Server Express)
- **Database Connector:** `mssql-django` with `pyodbc`
- **Driver:** Microsoft ODBC Driver 17 or 18 for SQL Server

### Server Prerequisites
1. **Python (v3.10+)**: Download from python.org. Ensure **"Add Python to PATH"** is selected during installation.
2. **Microsoft SQL Server**: Installed and running (Instance name e.g., `LOCALHOST\SQLEXPRESS`).
3. **Microsoft ODBC Driver 17 or 18 for SQL Server**: Required for Python to talk to SQL Server.
4. **SQL Server Management Studio (SSMS)**: Recommended for database operations.

---

## 3. 📂 Workspace Directory Structure

Below is the repository layout:

```text
c:\prc\HospProject\
├── HospProject/               # Django Core configuration module
│   ├── settings.py            # Global settings (DB, apps, middleware)
│   ├── urls.py                # Main URL router
│   └── wsgi.py                # WSGI entrypoint
├── hospApp/                   # Primary Hospital Application module
│   ├── models/                # Database models (Employee, DoctorConsultation, PatientVitals, etc.)
│   ├── views/                 # View logic & controller functions
│   ├── forms/                 # Form definitions
│   ├── templates/             # HTML templates (Doctor workbench, queue, history)
│   ├── static/                # Module static assets
│   ├── urls.py                # Hospital app URL routing
│   └── api_urls.py            # Web REST API endpoints
├── static/                    # Project-level static files
├── staticfiles/               # Collected static files (served by WhiteNoise in production)
├── media/                     # Uploaded files (patient records, prescriptions, lab scans)
├── build_for_hospital.py      # Automated build & bytecode compilation pipeline
├── generate_sql_data.py       # SQL seed data generator from live database
├── serve.py                   # Production server launcher using Waitress & WhiteNoise
├── run_on_startup.bat         # Interactive / manual server launch script
├── setup_autorun.bat          # Windows startup folder registration utility
├── hospital_db.sql            # Seed SQL script (roles, menus, departments, masters)
├── manage.py                  # Django CLI manager
├── .env                       # Local environment configuration file
└── .env.template              # Environment file template for deployment
```

---

## 4. ⚙️ Environment Configuration (`.env`)

Production settings are managed through environment variables stored in `.env`.

### `.env` Field Reference
```ini
# Security
SECRET_KEY=django-insecure-your-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100,*

# Database Connection (Microsoft SQL Server)
DB_HOST=LOCALHOST\SQLEXPRESS
DB_NAME=hospitalDatabase

# Authentication Options:
# 1. Windows Authentication: Leave DB_USER blank (trusted_connection=yes)
# 2. SQL Server Authentication: Provide DB_USER and DB_PASSWORD (trusted_connection=no)
DB_USER=sa
DB_PASSWORD=YourPassword123
```

---


## 5. 🗄️ Database Setup & Management

### Initial Database Creation (Fresh Setup)
1. Open **SQL Server Management Studio (SSMS)**.
2. Create a new database named **`hospitalDatabase`**.
3. Open Command Prompt in the project folder and run migrations:
   ```cmd
   python manage.py migrate
   ```
4. Seed initial lookup data:
   - In SSMS, open `hospital_db.sql`.
   - Ensure `hospitalDatabase` is selected and execute (**F5**).

### Seed Data Generator (`generate_sql_data.py`)
`generate_sql_data.py` extracts master configuration tables from a working database into `hospital_db.sql`.
- Preserves explicit Primary Key IDs using `SET IDENTITY_INSERT ON/OFF`.
- Exports master tables in dependency order (States, Districts, Employees, Roles, Main/Sub Menus, User Permissions, Departments, Case Types, Room/Bed Masters).

To generate a updated `hospital_db.sql`:
```cmd
python generate_sql_data.py
```

---

## 6. 📦 Production Build System (`build_for_hospital.py`)

To protect source code and prepare a deployment package, use `build_for_hospital.py`.

### What the Build Pipeline Does:
1. **Compiles Code:** Converts `.py` source files in `hospApp/` and `HospProject/` into Python bytecode (`.pyc`).
2. **Strips Source Code:** Removes `.py` files from the build directory (except required system entrypoints `manage.py`, `serve.py`, and package `__init__.py` files).
3. **Copies Assets:** Copies static files, media templates, `.env.template`, `hospital_db.sql`, and batch scripts.
4. **Validates Build:** Verifies zero source code leakage and reports build size.
5. **Generates ZIP Archive:** Archives `hospital_build/` into `hospital_build.zip` ready for USB distribution.

### Running the Build:
```cmd
python build_for_hospital.py
```
Output location: `c:\prc\HospProject\hospital_build\` and `hospital_build.zip`.

---

## 7. 🚀 Production Server Deployment & Autorun

### Step-by-Step Deployment Guide
1. **Transfer:** Copy `hospital_build` folder (or extract `hospital_build.zip`) to `C:\hospital_build` on the hospital server.
2. **Environment File:** Copy `.env.template` to `.env` and fill in DB host and allowed IPs.
3. **Dependencies:** Install requirements:
   ```cmd
   pip install -r requirements.txt
   ```
4. **Database:** Run `python manage.py migrate` and execute `hospital_db.sql` (if fresh installation).
5. **Configure Autorun:** Double-click `setup_autorun.bat` to register server auto-start in the Windows Startup folder (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`).
6. **Start Server:** Run `run_on_startup.bat` or execute `python serve.py`.

### Production WSGI Server (`serve.py`) Features
- Multi-threaded execution (`Waitress` with 4 worker threads).
- Static file serving via `WhiteNoise` from `staticfiles/`.
- Uploaded media file serving from `media/`.
- Resilient DB connection retry loop (up to 30 seconds wait for SQL Server service boot).

### Enabling Network (LAN) Access
1. Find Server IP: Run `ipconfig` in Command Prompt (e.g., `192.168.1.50`).
2. In **Windows Defender Firewall**, create an **Inbound Rule**:
   - Rule Type: **Port**
   - Protocol: **TCP**, Port: **8000**
   - Action: **Allow the connection**
3. Client Access URL: `http://192.168.1.50:8000`

---

## 8. 🔄 Live Server Update & Backup Procedures

### ⚠️ Critical Production Rules
> [!CAUTION]
> **DO NOT** execute `hospital_db.sql` on a live production server! It will overwrite live patient records and consultation history.
> **DO NOT** delete the `media/` directory! It contains live uploaded files, doctor prescriptions, and lab attachments.

### Safe Update Procedure:
1. Generate fresh build on development PC (`python build_for_hospital.py`).
2. Stop the live server on the target machine (`Ctrl+C` or terminate process).
3. Backup current live folder:
   ```cmd
   rename C:\hospital_build hospital_build_backup
   ```
4. Copy new `hospital_build` folder to `C:\hospital_build`.
5. Restore live configuration and patient upload files:
   ```cmd
   copy C:\hospital_build_backup\.env C:\hospital_build\.env
   xcopy C:\hospital_build_backup\media C:\hospital_build\media /E /I /H /Y
   ```
6. Install updated dependencies (if any): `pip install -r requirements.txt`.
7. Execute schema ALTER scripts in SSMS if database columns changed.
8. Restart server: `run_on_startup.bat`.

---

## 9. 🏥 Core Features & Web Workflows

### 1. Reception & Patient Registration
- Registers patient demographic data (UHID, Name, Age, Gender, Contact, Address).
- Generates sequential token numbers for doctor queues (`DoctorConsultation`).

### 2. Doctor Queue & Consultation Workbench
- **Waiting Queue:** Displays patients where `is_prescription_done = False`.
- **Completed Queue:** Displays patients where `is_prescription_done = True`.
- **Consultation Interface:** Allows entering vitals, medical observations, clinical diagnosis notes, lab investigation requests, and prescription medicines.
- Marks consultation completed automatically upon saving.

### 3. Patient Medical History
- Queries historic consultations, diagnoses, vitals, lab reports, and prescriptions using the patient's **UHID**.

---

## 10. 🔌 Web REST Integration Reference

The application exposes web endpoints for authentication, doctor profiles, consultation queue status, and patient medical history.

### Authentication & Session Management
- **Login Endpoint:** `POST /` (or `/login/`)
  - **Form Data:** `username`, `password`, `csrfmiddlewaretoken`
  - **Response:** `302 Found` with `Set-Cookie: sessionid=...`
- **Logout Endpoint:** `GET` / `POST /logout/`

### Doctor Profile API (`GET /api/doctor/profile/`)
Returns logged-in doctor profile and hospital master info:
```json
{
  "success": true,
  "doctor": {
    "doctor_id": "DOC101",
    "doctor_name": "Dr. Rajesh Kumar",
    "designation": "Senior Consultant",
    "department": "General Medicine",
    "role": "DOCTOR",
    "hospital": {
      "name": "City Care Hospital",
      "address": "123 Main Street, Sector 4",
      "phone": "+91 9876543210",
      "email": "info@citycarehosp.com"
    }
  }
}
```

### Patient & Vitals Endpoint (`GET /api/patient/consultation/<consult_id>/`)
Returns consultation info and vitals:
```json
{
  "success": true,
  "consultation_id": 452,
  "patient_details": {
    "patient_id": "PAT2026001",
    "uhid": "UHID98421",
    "name": "Ramesh Verma",
    "age": 45,
    "gender": "Male",
    "phone": "9876543210",
    "address": "House No 12, Gandhi Nagar",
    "visit_type": "New Visit",
    "consultation_type": "General OP"
  },
  "vitals": {
    "temperature": "98.6 °F",
    "bp": "120/80 mmHg",
    "pulse": "72 bpm",
    "spo2": "98%",
    "weight": "68.5 kg"
  }
}
```

### Patient Medical History Endpoint (`GET /api/patient/history/?uhid=<UHID>`)
Returns full visit timeline for a patient by UHID:
```json
{
  "success": true,
  "uhid": "UHID98421",
  "patient_name": "Ramesh Verma",
  "total_past_visits": 1,
  "medical_history": [
    {
      "consultation_id": 310,
      "visit_date": "2026-06-15",
      "doctor_name": "Dr. Rajesh Kumar",
      "department": "General Medicine",
      "vitals": {
        "bp": "130/85",
        "temp": "100.2 °F",
        "pulse": 80,
        "spo2": 97
      },
      "diagnosis_notes": "Acute Viral Fever with mild cough.",
      "prescription": {
        "medicines": "Tab. Paracetamol 650mg TDS (3 days)"
      }
    }
  ]
}
```

---
*Documentation compiled for Hospital Management System — Web & Server Architecture.*
