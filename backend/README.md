# 🏥 Hospital Management System - Backend Documentation

A clean, production-ready Django REST Framework (DRF) backend for the MediSetu Hospital Management System. It handles Authentication, Free Email OTP, Patient & Doctor Profiles, Smart Appointment Booking, Billing, Medical Records, Prescriptions, ML Disease Prediction, and Role-based Dashboards.

---

## 🌐 Live URLs & Admin Credentials

- **Live Base URL**: `https://hospital-management-system-ccc.onrender.com`
- **Django Admin Portal**: `https://hospital-management-system-ccc.onrender.com/admin/`

### 🔑 Pre-Configured Credentials

| Role | Username | Password | Email |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | `admin@hospital.com` |
| **Doctor** | `dr_smith` | `doctor123` | `smith@hospital.com` |
| **Patient** | `john_doe` | `patient123` | `john@example.com` |

---

## 🛠️ Tech Stack & Dependencies

- **Framework**: Django 5.x & Django REST Framework (DRF)
- **Authentication**: SimpleJWT (`JWT Access + Refresh Tokens`)
- **Database**: SQLite (Local Dev) / PostgreSQL (Cloud via `DATABASE_URL`)
- **Email Driver**: SMTP Gmail App Password (`django.core.mail`)
- **CORS Headers**: Fully configured for Vercel Frontend (`CORS_ALLOW_ALL_ORIGINS = True`)
- **WSGI / Server**: Gunicorn & WhiteNoise (Static files)

---

## 📡 Complete API Reference

### 1. 🔐 Authentication & OTP

| Endpoint | Method | Public / Auth | Description & Required Body |
|---|---|---|---|
| `/api/auth/send-otp/` | `POST` | Public | Send 6-digit OTP: `{"email": "user@gmail.com"}` |
| `/api/auth/verify-otp/` | `POST` | Public | Verify OTP: `{"email": "user@gmail.com", "otp": "123456"}` |
| `/api/auth/register/` | `POST` | Public | Register User: `{"username", "email", "password", "role": "PATIENT"}` |
| `/api/auth/login/` | `POST` | Public | Login: `{"username", "password"}` -> Returns JWT Tokens & User Object |
| `/api/auth/refresh/` | `POST` | Public | Refresh Access Token: `{"refresh": "<refresh_token>"}` |
| `/api/auth/me/` | `GET` | Bearer Auth | Get Logged-in User Info |

---

### 2. 👨‍⚕️ Doctors APIs

| Endpoint | Method | Public / Auth | Description |
|---|---|---|---|
| `/api/doctors/` | `GET` | Public | List all doctors, specializations, fees & schedules |
| `/api/doctors/<id>/` | `GET` | Public | View single doctor profile details |
| `/api/doctors/profile/` | `GET`/`PUT` | Doctor Auth | View or Update logged-in doctor's specialization, fee, shift schedule |

---

### 3. 👤 Patients APIs

| Endpoint | Method | Public / Auth | Description |
|---|---|---|---|
| `/api/patients/profile/` | `GET`/`PUT` | Patient Auth | View or Update patient profile (`first_name`, `last_name`, `email`, `phone`, `date_of_birth`, `gender`, `blood_group`, `address`, `allergies`, `emergency_contact`) |
| `/api/patients/<id>/` | `GET` | Admin/Doctor | View specific patient details |
| `/api/patients/` | `GET` | Admin/Doctor | List all registered patients |

---

### 4. 📅 Smart Appointment Booking

| Endpoint | Method | Public / Auth | Description |
|---|---|---|---|
| `/api/appointments/` | `POST` | Bearer Auth | Book Appointment: `{"doctor_id": 1, "appointment_date": "2026-10-15", "appointment_time": "10:30:00", "reason": "Fever"}` |
| `/api/appointments/` | `GET` | Bearer Auth | List Appointments. Filters: `?upcoming=true`, `?status=BOOKED` |
| `/api/appointments/<id>/` | `GET`/`PUT`/`DELETE` | Bearer Auth | Detail, Update Status (`BOOKED`, `COMPLETED`, `CANCELLED`), or Delete |

---

### 5. 🤖 ML Disease Prediction & Reports

| Endpoint | Method | Public / Auth | Description |
|---|---|---|---|
| `/api/predict-disease/` | `POST` | Bearer Auth | Predict Disease: `{"symptoms": "Fever, chest pain", "report_file": <PDF/Image>}` |
| `/api/medical-records/` | `GET`/`POST` | Bearer Auth | List or Create Medical Record with Diagnosis & uploaded PDF/Image report |

---

### 6. 💊 Prescriptions & Billing

| Endpoint | Method | Public / Auth | Description |
|---|---|---|---|
| `/api/prescriptions/` | `GET`/`POST` | Bearer Auth | List or Create Prescriptions (`medicine_name`, `dosage`, `duration`) |
| `/api/bills/` | `GET`/`POST` | Bearer Auth | List or Create Bills |
| `/api/bills/<id>/` | `PUT` | Bearer Auth | Update Bill status (`status`: `"PAID"`) |

---

### 7. 📊 Dashboards

| Endpoint | Method | Auth Required | Returns |
|---|---|---|---|
| `/api/dashboard/patient/` | `GET` | Patient Auth | Upcoming appointments count, history count, recent prescriptions, pending bills |
| `/api/dashboard/doctor/` | `GET` | Doctor Auth | Today's appointments count, total patients, recent bookings |
| `/api/dashboard/admin/` | `GET` | Admin Auth | Platform-wide totals (Doctors, Patients, Appointments, Revenue) |

---

## ⚙️ Local Development Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Run local development server
python manage.py runserver
```

Server runs locally at: `http://127.0.0.1:8000/`

---

## 🔒 Security & Authorization Header

All authenticated endpoints require the JWT Access token passed in request headers:

```http
Authorization: Bearer <YOUR_JWT_ACCESS_TOKEN>
Content-Type: application/json
```
