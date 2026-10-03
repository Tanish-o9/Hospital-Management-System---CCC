# Hospital Management System Backend (Single-App Django Architecture)

A minimal, clean, and beginner-friendly Django & Django REST Framework (DRF) backend implementing a complete Hospital & Clinic Management System inside a single application `hospital`.

---

## 📁 Project Structure

```
hospital_management/
├── manage.py
├── requirements.txt
├── .env.example
├── .env
├── seed_demo_data.py
├── README.md
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── hospital/
    ├── migrations/
    │   └── 0001_initial.py
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── permissions.py
    └── tests.py
```

---

## 🛠 Tech Stack

- **Framework**: Django 5.x & Django REST Framework (DRF)
- **Authentication**: SimpleJWT (`djangorestframework-simplejwt`)
- **Database**: PostgreSQL (if `DATABASE_URL` is set in `.env`), otherwise SQLite.
- **Environment Management**: `python-dotenv` & `dj-database-url`
- **CORS**: `django-cors-headers`

---

## ⚙️ Setup & Installation

### 1. Clone & Activate Virtual Environment

```bash
cd hospital_management
python -m venv .venv

# Activate:
# Windows:
..\.venv\Scripts\activate
# Linux/macOS:
source ../.venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations

```bash
python manage.py makemigrations hospital
python manage.py migrate
```

### 4. Seed Demo Data (Optional)

Populate default demo users (Admin, Doctor, Patient) and sample appointment/record data:

```bash
python seed_demo_data.py
```

### 5. Run Unit Tests

```bash
python manage.py test hospital
```

### 6. Start Development Server

```bash
python manage.py runserver
```
The server will run at: `http://127.0.0.1:8000/`

---

## 🔑 Pre-Configured Test Credentials

| Role | Username | Password | Email |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | `admin@hospital.com` |
| **Doctor** | `dr_smith` | `doctor123` | `smith@hospital.com` |
| **Patient** | `john_doe` | `patient123` | `john@example.com` |

---

## 📡 API Endpoints List

### 1. Authentication & Free Email OTP
- `POST /api/auth/send-otp/` - Send 6-digit OTP to user's email (`{ "email": "user@example.com" }`)
- `POST /api/auth/verify-otp/` - Verify OTP (`{ "email": "user@example.com", "otp": "123456" }`)
- `POST /api/auth/register/` - Register Doctor or Patient (`role`: `DOCTOR` | `PATIENT`, optional patient field: `date_of_birth`/`dob`, optional doctor fields: `specialization`, `qualification`, `experience`, `consultation_fee`, `phone`, `available_days`)
- `POST /api/auth/login/` - Login & receive JWT access + refresh tokens
- `POST /api/auth/refresh/` - Refresh JWT access token
- `GET  /api/auth/me/` - Retrieve authenticated user profile

### 2. Doctor Management
- `GET  /api/doctors/` - List all doctors
- `GET  /api/doctors/my-profile/` - View current doctor's profile
- `POST /api/doctors/profile/` - Create doctor profile
- `PUT  /api/doctors/profile/` - Update current doctor's profile
- `GET  /api/doctors/<int:pk>/` - View specific doctor profile

### 3. Patient Management
- `GET  /api/patients/` - List all patients (Doctors & Admins)
- `GET  /api/patients/my-profile/` - View current patient's profile
- `POST /api/patients/profile/` - Create patient profile
- `PUT  /api/patients/profile/` - Update current patient's profile
- `GET  /api/patients/<int:pk>/` - View specific patient profile

### 4. Appointments
- `GET  /api/appointments/` - List appointments. Filters: `?status=BOOKED`, `?upcoming=true`
- `POST /api/appointments/` - Book an appointment (Auto-generates Bill)
- `GET  /api/appointments/<int:pk>/` - View appointment details
- `PUT  /api/appointments/<int:pk>/` - Update appointment status (`BOOKED`, `COMPLETED`, `CANCELLED`)
- `DELETE /api/appointments/<int:pk>/` - Cancel/Delete appointment

### 5. Medical Records
- `GET  /api/medical-records/` - List medical records
- `POST /api/medical-records/` - Create medical record (Doctors & Admins)
- `GET  /api/medical-records/<int:pk>/` - View medical record details
- `PUT  /api/medical-records/<int:pk>/` - Update medical record (Doctors & Admins)

### 6. Prescriptions
- `GET  /api/prescriptions/` - List prescriptions
- `POST /api/prescriptions/` - Create prescription (Doctors & Admins)
- `GET  /api/prescriptions/<int:pk>/` - View prescription details
- `PUT  /api/prescriptions/<int:pk>/` - Update prescription (Doctors & Admins)

### 7. Billing
- `GET  /api/bills/` - List bills
- `POST /api/bills/` - Create bill manually (Uses doctor consultation fee)
- `GET  /api/bills/<int:pk>/` - View bill details
- `PUT  /api/bills/<int:pk>/` - Update bill status (`PENDING` | `PAID`)

### 8. Dashboards
- `GET /api/dashboard/doctor/` - Doctor metrics (total/upcoming/completed appointments, patient count, recent list)
- `GET /api/dashboard/patient/` - Patient metrics (upcoming appointments, appointment history count, recent prescriptions, pending/total bills)
- `GET /api/dashboard/admin/` - Platform-wide statistics (doctors, patients, appointments, billing totals)
