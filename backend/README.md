# 📌 MediSetu Hospital Backend API Documentation

## 🌐 BASE URL

```text
https://hospital-management-system-ccc.onrender.com
```

---

## 1. Auth Routes (`/api/auth`)

### ◆ Route 1.1: Send Email OTP

- **Method**: `POST`
- **Endpoint**: `/api/auth/send-otp/`
- **Auth Required**: `NO`
- **Request Body Example**:
  ```json
  {
    "email": "tanishrajput673@gmail.com"
  }
  ```
- **Response Type (`200 OK`)**:
  ```json
  {
    "message": "OTP sent successfully to email.",
    "email": "tanishrajput673@gmail.com"
  }
  ```

---

### ◆ Route 1.2: Verify Email OTP

- **Method**: `POST`
- **Endpoint**: `/api/auth/verify-otp/`
- **Auth Required**: `NO`
- **Request Body Example**:
  ```json
  {
    "email": "tanishrajput673@gmail.com",
    "otp": "123456"
  }
  ```
- **Response Type (`200 OK`)**:
  ```json
  {
    "message": "OTP verified successfully.",
    "email": "tanishrajput673@gmail.com",
    "is_verified": true
  }
  ```

---

### ◆ Route 1.3: User Registration (Sign Up)

- **Method**: `POST`
- **Endpoint**: `/api/auth/register/`
- **Auth Required**: `NO`
- **Request Body Example**:
  ```json
  {
    "username": "tanish_kumar",
    "email": "tanishrajput673@gmail.com",
    "password": "password123",
    "first_name": "Tanish",
    "last_name": "Kumar",
    "role": "PATIENT",
    "date_of_birth": "2008-10-17"
  }
  ```
- **Response Type (`201 Created`)**:
  ```json
  {
    "message": "User registered successfully.",
    "user": {
      "id": 3,
      "username": "tanish_kumar",
      "email": "tanishrajput673@gmail.com",
      "first_name": "Tanish",
      "last_name": "Kumar",
      "role": "PATIENT",
      "patient_profile": {
        "id": 1,
        "date_of_birth": "2008-10-17",
        "gender": null,
        "phone": null,
        "blood_group": null
      }
    }
  }
  ```

---

### ◆ Route 1.4: User Sign In (Login)

- **Method**: `POST`
- **Endpoint**: `/api/auth/login/`
- **Auth Required**: `NO`
- **Request Body Example**:
  ```json
  {
    "username": "john_doe",
    "password": "patient123"
  }
  ```
- **Response Type (`200 OK`)**:
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 3,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "PATIENT"
    }
  }
  ```

---

### ◆ Route 1.5: Refresh JWT Token

- **Method**: `POST`
- **Endpoint**: `/api/auth/refresh/`
- **Auth Required**: `NO`
- **Request Body Example**:
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **Response Type (`200 OK`)**:
  ```json
  {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```

---

### ◆ Route 1.6: Get Current User Profile

- **Method**: `GET`
- **Endpoint**: `/api/auth/me/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**: `None`
- **Response Type (`200 OK`)**:
  ```json
  {
    "id": 3,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "PATIENT",
    "patient_profile": {
      "id": 1,
      "date_of_birth": "1990-05-15",
      "gender": "Male",
      "phone": "+9876543210",
      "address": "123 Main Street, NY",
      "blood_group": "O+"
    }
  }
  ```

---

## 2. Doctor Routes (`/api/doctors`)

### ◆ Route 2.1: Get All Doctors

- **Method**: `GET`
- **Endpoint**: `/api/doctors/`
- **Auth Required**: `NO`
- **Request Body Example**: `None`
- **Response Type (`200 OK`)**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": 1,
        "user": {
          "id": 2,
          "username": "dr_smith",
          "email": "smith@hospital.com",
          "first_name": "John",
          "last_name": "Smith",
          "role": "DOCTOR"
        },
        "specialization": "Cardiology",
        "phone": "+1234567890",
        "qualification": "MBBS, MD (Cardiology)",
        "experience": 10,
        "consultation_fee": "750.00",
        "available_days": "Monday to Friday",
        "available_from": "09:00:00",
        "available_to": "17:00:00"
      }
    ]
  }
  ```

---

### ◆ Route 2.2: Get Doctor by ID

- **Method**: `GET`
- **Endpoint**: `/api/doctors/:doctorId/`
- **Auth Required**: `NO`
- **Request Body Example**: `None`
- **Response Type (`200 OK`)**:
  ```json
  {
    "id": 1,
    "user": {
      "id": 2,
      "username": "dr_smith",
      "email": "smith@hospital.com",
      "first_name": "John",
      "last_name": "Smith",
      "role": "DOCTOR"
    },
    "specialization": "Cardiology",
    "phone": "+1234567890",
    "qualification": "MBBS, MD (Cardiology)",
    "experience": 10,
    "consultation_fee": "750.00",
    "available_days": "Monday to Friday",
    "available_from": "09:00:00",
    "available_to": "17:00:00"
  }
  ```

---

### ◆ Route 2.3: Update Doctor Profile

- **Method**: `PUT`
- **Endpoint**: `/api/doctors/profile/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**:
  ```json
  {
    "specialization": "Cardiology & Surgery",
    "consultation_fee": 850.00,
    "experience": 12
  }
  ```
- **Response Type (`200 OK`)**:
  ```json
  {
    "id": 1,
    "specialization": "Cardiology & Surgery",
    "consultation_fee": "850.00",
    "experience": 12
  }
  ```

---

## 3. Patient Profile Routes (`/api/patients`)

### ◆ Route 3.1: Get / Update My Patient Profile

- **Method**: `PUT`
- **Endpoint**: `/api/patients/profile/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**:
  ```json
  {
    "first_name": "Tanish",
    "last_name": "Kumar",
    "email": "tanishrajput673@gmail.com",
    "phone": "+917668638105",
    "date_of_birth": "2008-10-17",
    "gender": "Male",
    "blood_group": "B+",
    "address": "Delhi, India",
    "allergies": "Penicillin, Dust",
    "emergency_contact": "+919876543210"
  }
  ```
- **Response Type (`200 OK`)**:
  ```json
  {
    "id": 1,
    "user": {
      "id": 3,
      "username": "tanish_kumar",
      "email": "tanishrajput673@gmail.com",
      "first_name": "Tanish",
      "last_name": "Kumar",
      "role": "PATIENT"
    },
    "date_of_birth": "2008-10-17",
    "gender": "Male",
    "phone": "+917668638105",
    "address": "Delhi, India",
    "blood_group": "B+",
    "allergies": "Penicillin, Dust",
    "emergency_contact": "+919876543210"
  }
  ```

---

## 4. Appointment Routes (`/api/appointments`)

### ◆ Route 4.1: Book an Appointment

- **Method**: `POST`
- **Endpoint**: `/api/appointments/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**:
  ```json
  {
    "doctor_id": 1,
    "appointment_date": "2026-10-15",
    "appointment_time": "10:30:00",
    "reason": "Routine heart checkup and fever"
  }
  ```
- **Response Type (`201 Created`)**:
  ```json
  {
    "id": 5,
    "patient": 1,
    "patient_detail": {
      "id": 1,
      "user": {
        "id": 3,
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe"
      }
    },
    "doctor": 1,
    "doctor_detail": {
      "id": 1,
      "specialization": "Cardiology",
      "consultation_fee": "750.00"
    },
    "appointment_date": "2026-10-15",
    "appointment_time": "10:30:00",
    "reason": "Routine heart checkup and fever",
    "status": "BOOKED",
    "created_at": "2026-10-04T17:22:00.000Z"
  }
  ```

---

### ◆ Route 4.2: Get My Appointments

- **Method**: `GET`
- **Endpoint**: `/api/appointments/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**: `None`
- **Response Type (`200 OK`)**:
  ```json
  [
    {
      "id": 5,
      "appointment_date": "2026-10-15",
      "appointment_time": "10:30:00",
      "reason": "Routine heart checkup and fever",
      "status": "BOOKED"
    }
  ]
  ```

---

### ◆ Route 4.3: Update Appointment Status

- **Method**: `PUT`
- **Endpoint**: `/api/appointments/:appointmentId/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**:
  ```json
  {
    "status": "COMPLETED"
  }
  ```
- **Response Type (`200 OK`)**:
  ```json
  {
    "id": 5,
    "status": "COMPLETED"
  }
  ```

---

## 5. Medical Record Routes (`/api/medical-records`)

### ◆ Route 5.1: Get Medical Records

- **Method**: `GET`
- **Endpoint**: `/api/medical-records/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**: `None`
- **Response Type (`200 OK`)**:
  ```json
  [
    {
      "id": 1,
      "patient": 1,
      "doctor": 1,
      "diagnosis": "Mild Hypertension",
      "doctor_notes": "Patient advised low sodium diet and regular exercise.",
      "report_file": null,
      "created_at": "2026-10-04T16:33:21Z"
    }
  ]
  ```

---

### ◆ Route 5.2: Create Medical Record

- **Method**: `POST`
- **Endpoint**: `/api/medical-records/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**:
  ```json
  {
    "patient_id": 1,
    "diagnosis": "Acute Bronchitis",
    "doctor_notes": "Prescribed antibiotics and bed rest."
  }
  ```
- **Response Type (`201 Created`)**:
  ```json
  {
    "id": 2,
    "diagnosis": "Acute Bronchitis",
    "doctor_notes": "Prescribed antibiotics and bed rest.",
    "created_at": "2026-10-04T22:30:00Z"
  }
  ```

---

## 6. Prescriptions & Billing Routes

### ◆ Route 6.1: Get Prescriptions

- **Method**: `GET`
- **Endpoint**: `/api/prescriptions/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**: `None`
- **Response Type (`200 OK`)**:
  ```json
  [
    {
      "id": 1,
      "medicine_name": "Multivitamin Tabs 500mg",
      "dosage": "Once daily after meal",
      "duration": "15 days",
      "instructions": "Take with water."
    }
  ]
  ```

---

### ◆ Route 6.2: Get Bills

- **Method**: `GET`
- **Endpoint**: `/api/bills/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**: `None`
- **Response Type (`200 OK`)**:
  ```json
  [
    {
      "id": 1,
      "consultation_fee": "750.00",
      "amount": "750.00",
      "status": "PENDING"
    }
  ]
  ```

---

### ◆ Route 6.3: Pay Bill

- **Method**: `PUT`
- **Endpoint**: `/api/bills/:billId/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**:
  ```json
  {
    "status": "PAID"
  }
  ```
- **Response Type (`200 OK`)**:
  ```json
  {
    "id": 1,
    "amount": "750.00",
    "status": "PAID"
  }
  ```

---

## 7. Dashboard Analytics Routes (`/api/dashboard`)

### ◆ Route 7.1: Get Patient Dashboard Overview

- **Method**: `GET`
- **Endpoint**: `/api/dashboard/patient/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**: `None`
- **Response Type (`200 OK`)**:
  ```json
  {
    "upcoming_appointments": 1,
    "appointment_history_count": 1,
    "recent_prescriptions": [
      {
        "id": 1,
        "medicine_name": "Multivitamin Tabs 500mg",
        "dosage": "Once daily after meal",
        "duration": "15 days"
      }
    ],
    "pending_bills": 1,
    "total_bills": 1
  }
  ```

---

### ◆ Route 7.2: Get Doctor Dashboard Overview

- **Method**: `GET`
- **Endpoint**: `/api/dashboard/doctor/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**: `None`
- **Response Type (`200 OK`)**:
  ```json
  {
    "total_appointments": 5,
    "upcoming_appointments": 2,
    "completed_appointments": 3,
    "total_patients": 4,
    "recent_appointments": []
  }
  ```

---

## 8. ML Disease Prediction Route (`/api/predict-disease`)

### ◆ Route 8.1: Predict Disease from Symptoms & Report File

- **Method**: `POST`
- **Endpoint**: `/api/predict-disease/`
- **Auth Required**: `YES (Authorization: Bearer <TOKEN>)`
- **Request Body Example**:
  ```json
  {
    "symptoms": "High fever, persistent cough, chest congestion"
  }
  ```
- **Response Type (`200 OK`)**:
  ```json
  {
    "predicted_disease": "Analysis for: High fever, persistent cough, chest congestion",
    "confidence": "92.0%",
    "recommendation": "Consult specialist for detailed examination.",
    "medical_record_id": 2
  }
  ```
