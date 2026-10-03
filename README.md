# Hospital & Clinic Management System Backend

A simple, clean, and human-readable Django & Django REST Framework (DRF) backend API for managing hospital operations, including Authentication, Doctor Profiles, Patient Profiles, Appointments, Medical Records, Prescriptions, Billing, and Role-Based Dashboards.

---

## 🛠 Tech Stack

- **Framework**: Django 5.x & Django REST Framework (DRF)
- **Authentication**: SimpleJWT (JSON Web Tokens)
- **Database**: PostgreSQL (if `DATABASE_URL` is configured in `.env`), otherwise SQLite.
- **Environment Management**: `python-dotenv` & `dj-database-url`
- **CORS**: `django-cors-headers`

---

## 📁 Project Structure

```
Hospital Management System/
└── backend/
    ├── manage.py
    ├── requirements.txt
    ├── .env.example
    ├── .env
    ├── seed_demo_data.py
    ├── README.md
    ├── config/
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    └── hospital/
        ├── models.py      # Custom User Model, Doctor & Patient Profiles, Appointments, Records, Bills
        ├── views.py       # DRF API Views for Auth, Profiles, Bookings, Dashboard
        ├── serializers.py # DRF Serializers
        ├── permissions.py # Custom IsDoctor, IsPatient, IsAdmin permissions
        ├── urls.py        # App URL Router
        └── tests.py       # Automated APITestCase Suite
```

---

## ⚙️ Environment Variables

Create a `.env` file in the `backend/` directory (copy from `backend/.env.example`):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=*

# Optional: PostgreSQL Database connection string
# DATABASE_URL=postgres://username:password@localhost:5432/hospital_db
```

---

## 🚀 Installation & Setup Guide

### 1. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies & Run Migrations

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
```

### 3. Seed Demo Data (Optional)

Populate default demo users (Admin, Doctor, Patient) and sample records:

```bash
python seed_demo_data.py
```

### 4. Run Development Server

```bash
python manage.py runserver
```
The server will be available at: `http://127.0.0.1:8000/`

---

## 🔑 Pre-Configured Test Users (from Seeding)

| Role | Username | Password | Email |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | `admin@hospital.com` |
| **Doctor** | `dr_smith` | `doctor123` | `smith@hospital.com` |
| **Patient** | `john_doe` | `patient123` | `john@example.com` |

---

## 📡 API Endpoints Overview

### 1. Authentication & Free Email OTP (`/api/auth/`)
- `POST /api/auth/send-otp/` - Send 6-digit OTP to user's email (`{ "email": "user@example.com" }`)
- `POST /api/auth/verify-otp/` - Verify OTP (`{ "email": "user@example.com", "otp": "123456" }`)
- `POST /api/auth/register/` - Register Doctor or Patient (`role`: `DOCTOR` | `PATIENT`, optional patient field: `date_of_birth`/`dob`, optional doctor fields: `specialization`, `qualification`, `experience`, `consultation_fee`, `phone`, `available_days`)
- `POST /api/auth/login/` - Obtain JWT Access & Refresh tokens
- `POST /api/auth/refresh/` - Refresh JWT Access token
- `GET  /api/auth/me/` - Get current user profile & role details

### 2. Doctor Management (`/api/doctors/`)
- `GET  /api/doctors/` - List all doctors (Patients, Doctors & Admins)
- `GET  /api/doctors/my-profile/` - View current doctor's profile
- `POST /api/doctors/profile/` - Create doctor profile
- `PUT  /api/doctors/profile/` - Update current doctor's profile
- `GET  /api/doctors/<id>/` - Retrieve specific doctor details

### 3. Patient Management (`/api/patients/`)
- `GET  /api/patients/` - List all patients (Doctors & Admins)
- `GET  /api/patients/my-profile/` - View current patient's profile
- `POST /api/patients/profile/` - Create patient profile
- `PUT  /api/patients/profile/` - Update current patient's profile
- `GET  /api/patients/<id>/` - Retrieve specific patient details

### 4. Appointments (`/api/appointments/`)
- `GET  /api/appointments/` - List appointments (filtered by user role). Query params: `?status=BOOKED`, `?upcoming=true`
- `POST /api/appointments/` - Book an appointment (Auto-creates associated Bill)
- `GET  /api/appointments/<id>/` - View specific appointment details
- `PUT  /api/appointments/<id>/` - Update appointment status (`BOOKED`, `COMPLETED`, `CANCELLED`)
- `DELETE /api/appointments/<id>/` - Delete appointment

### 5. Medical Records (`/api/medical-records/`)
- `GET  /api/medical-records/` - List medical records
- `POST /api/medical-records/` - Create medical record (Doctors & Admins)
- `GET  /api/medical-records/<id>/` - View medical record
- `PUT  /api/medical-records/<id>/` - Update medical record (Doctors & Admins)

### 6. Prescriptions (`/api/prescriptions/`)
- `GET  /api/prescriptions/` - List prescriptions
- `POST /api/prescriptions/` - Create prescription (Doctors & Admins)
- `GET  /api/prescriptions/<id>/` - View prescription details
- `PUT  /api/prescriptions/<id>/` - Update prescription (Doctors & Admins)

### 7. Billing (`/api/billing/` / `/api/bills/`)
- `GET  /api/bills/` - List bills (Patients see theirs, Doctors/Admins see relevant bills)
- `POST /api/bills/` - Create bill manually (Uses doctor consultation fee by default)
- `GET  /api/bills/<id>/` - View bill details
- `PUT  /api/bills/<id>/` - Update bill status (`PENDING` | `PAID`)

### 8. Dashboards (`/api/dashboard/`)
- `GET /api/dashboard/doctor/` - Total/upcoming/completed appointments, total patients, recent appointments
- `GET /api/dashboard/patient/` - Upcoming appointments, total history, recent prescriptions, pending/total bills
- `GET /api/dashboard/admin/` - Platform metrics (doctors, patients, appointments, billing totals)
