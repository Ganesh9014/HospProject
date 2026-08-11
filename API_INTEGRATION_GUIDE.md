# 🏥 HOSPITAL MANAGEMENT SYSTEM - TECHNICAL & API INTEGRATION GUIDE

This document provides a comprehensive technical overview and API reference for integrating with the Hospital Management System. It covers Authentication, Doctor Profile, Patient Queue Management, Vitals, and Medical History.

---

## 1. 🔑 Authentication & Session Management

The web application uses standard Django Session Authentication (`sessionid` cookie).

### A. Login Endpoint
- **URL:** `http://127.0.0.1:8000/` (or `/login/`)
- **HTTP Method:** `POST`
- **Content-Type:** `application/x-www-form-urlencoded`
- **Request Parameters:**
  ```text
  csrfmiddlewaretoken=<csrf_token>
  username=<username>
  password=<password>
  remember_me=on (optional)
  ```
- **Response Handling:**
  - **On Success:** `302 Found` (Redirects to `/home/`) with `Set-Cookie: sessionid=...` header.
  - **On Failure:** `200 OK` (Renders login page with an error message).

### B. Session & Logout
- **Logout Endpoint:** `GET` or `POST` `http://127.0.0.1:8000/logout/`
- **Session Duration:** 10 minutes default (`SESSION_COOKIE_AGE = 600`).
- **Identification:** Every incoming HTTP request includes the `sessionid` cookie. Django retrieves the logged-in user automatically via `request.user` and `request.session['username']`.

---

## 2. 👨‍⚕️ Doctor Details & Profile

In this system, a **Doctor** is an **Employee** (`Employee` model) linked to a user permission account (`Tbluserpermission`).

### Field Mapping
| Information | Database Field / Source |
| :--- | :--- |
| **Doctor / User ID** | `Tbluserpermission.empid` or `Tbluserpermission.username` |
| **Doctor Name** | `Tbluserpermission.empname` |
| **Department / Specialization** | `Tbluserpermission.department` / `Tbluserpermission.empdesig` |
| **Role** | `Tbluserpermission.mainrole.rolename` |
| **Hospital Details** | `HospitalMaster` (`name`, `address`, `phone`, `email`) |

### Doctor Profile API Endpoint (`GET /api/doctor/profile/`)
**Sample JSON Response:**
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

---

## 3. 📋 Patient Queue Management

### Patient Status Flow
```
[ Registered at Front Office ]
               │
               ▼
   1. Waiting (is_prescription_done = False)
               │
               ▼  (Doctor selects patient from queue)
   2. In Consultation (Record Opened)
               │
               ▼  (Doctor saves prescription)
   3. Completed (is_prescription_done = True)
```

### Queue Definitions & Filter Rules
- **Today's Assigned Patients:** `DoctorConsultation.objects.filter(isactive='Y', createddate__date=today)`
- **Waiting Patients:** `DoctorConsultation.objects.filter(isactive='Y', is_prescription_done=False)`
- **Completed Patients:** `DoctorConsultation.objects.filter(isactive='Y', is_prescription_done=True)`
- **Token Number:** `DoctorConsultation.tokenno` (auto-assigned sequentially during registration)
- **Patient Department:** `DoctorConsultation.casetypemaster` / `Tbluserpermission.department`

### Status Update Logic
When a doctor completes a consultation:
```python
consult = DoctorConsultation.objects.get(id=consult_id)
consult.is_prescription_done = True
consult.save()
```

---

## 4. 🩺 Patient Details & Vitals

When a doctor opens a patient from the queue, demography and vitals are populated automatically from `DoctorConsultation` and `PatientVitals`.

### Patient & Vitals Endpoint (`GET /api/patient/consultation/<consult_id>/`)
**Sample JSON Response:**
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
    "consultation_type": "General OP",
    "registration_date": "2026-08-11T10:15:00"
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

---

## 5. 📜 Previous Medical History

Historical consultations, prescriptions, diagnoses, and lab reports are queried using the patient's unique **UHID**.

### Patient Medical History Endpoint (`GET /api/patient/history/?uhid=UHID98421`)
**Sample JSON Response:**
```json
{
  "success": true,
  "uhid": "UHID98421",
  "patient_name": "Ramesh Verma",
  "total_past_visits": 2,
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
        "medicines": "Tab. Paracetamol 650mg TDS (3 days), Syrup Ascoril 10ml BD",
        "recognized_text": "Pt complains of fever x 2 days. Advised rest & hydration.",
        "next_visit_date": "2026-06-20"
      },
      "lab_investigations": [
        {
          "test_name": "Complete Blood Count (CBC)",
          "status": "Completed",
          "date": "2026-06-15"
        }
      ]
    },
    {
      "consultation_id": 180,
      "visit_date": "2026-01-10",
      "doctor_name": "Dr. Ananya Sharma",
      "department": "Dermatology",
      "vitals": {
        "bp": "118/78",
        "temp": "98.4 °F",
        "pulse": 74,
        "spo2": 99
      },
      "diagnosis_notes": "Allergic Contact Dermatitis on left arm.",
      "prescription": {
        "medicines": "Calamine Lotion application BD, Tab Cetirizine 10mg HS",
        "recognized_text": "Avoid soap contact.",
        "next_visit_date": null
      },
      "lab_investigations": []
    }
  ]
}
```
