import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from hospital.models import DoctorProfile, PatientProfile, Appointment, Bill, MedicalRecord, Prescription
from datetime import date, time

User = get_user_model()

print("Seeding demo data for single-app hospital_management project...")

# 1. Admin
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@hospital.com',
        'first_name': 'System',
        'last_name': 'Admin',
        'role': User.Role.ADMIN,
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print("Created Admin user: admin / admin123")

# 2. Doctor
doc_user, created = User.objects.get_or_create(
    username='dr_smith',
    defaults={
        'email': 'smith@hospital.com',
        'first_name': 'John',
        'last_name': 'Smith',
        'role': User.Role.DOCTOR
    }
)
if created:
    doc_user.set_password('doctor123')
    doc_user.save()
    print("Created Doctor user: dr_smith / doctor123")

doc_profile, _ = DoctorProfile.objects.get_or_create(
    user=doc_user,
    defaults={
        'specialization': 'Cardiology',
        'phone': '+1234567890',
        'qualification': 'MBBS, MD (Cardiology)',
        'experience': 10,
        'consultation_fee': 750.00,
        'available_days': 'Monday to Friday',
        'available_from': time(9, 0),
        'available_to': time(17, 0)
    }
)

# 3. Patient
patient_user, created = User.objects.get_or_create(
    username='john_doe',
    defaults={
        'email': 'john@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'role': User.Role.PATIENT
    }
)
if created:
    patient_user.set_password('patient123')
    patient_user.save()
    print("Created Patient user: john_doe / patient123")

patient_profile, _ = PatientProfile.objects.get_or_create(
    user=patient_user,
    defaults={
        'date_of_birth': date(1990, 5, 15),
        'gender': 'Male',
        'phone': '+9876543210',
        'address': '123 Main Street, NY',
        'blood_group': 'O+',
        'allergies': 'Penicillin',
        'emergency_contact': '+1122334455'
    }
)

# 4. Appointment
appointment, created = Appointment.objects.get_or_create(
    patient=patient_profile,
    doctor=doc_profile,
    appointment_date=date.today(),
    appointment_time=time(10, 0),
    defaults={
        'reason': 'Routine heart checkup',
        'status': Appointment.Status.BOOKED
    }
)
if created:
    print("Created Appointment for John Doe with Dr. Smith")
    Bill.objects.create(
        patient=patient_profile,
        doctor=doc_profile,
        appointment=appointment,
        consultation_fee=doc_profile.consultation_fee,
        amount=doc_profile.consultation_fee,
        status=Bill.Status.PENDING
    )
    print("Generated Bill for Appointment")

# 5. Medical Record
MedicalRecord.objects.get_or_create(
    patient=patient_profile,
    doctor=doc_profile,
    appointment=appointment,
    defaults={
        'diagnosis': 'Mild Hypertension',
        'doctor_notes': 'Patient advised low sodium diet and regular daily exercise.'
    }
)

# 6. Prescription
Prescription.objects.get_or_create(
    patient=patient_profile,
    doctor=doc_profile,
    appointment=appointment,
    medicine_name='Amlodipine 5mg',
    defaults={
        'dosage': 'Once daily after breakfast',
        'duration': '30 days',
        'instructions': 'Monitor blood pressure weekly.'
    }
)

print("Demo data seeded successfully for single-app hospital_management project!")
