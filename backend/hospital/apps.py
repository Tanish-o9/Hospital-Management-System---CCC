from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_admin(sender, **kwargs):
    try:
        from django.contrib.auth import get_user_model
        from hospital.models import DoctorProfile, PatientProfile
        User = get_user_model()

        # 1. Admin
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            User.objects.create_superuser(
                username='admin',
                email='admin@hospital.com',
                password='admin123',
                first_name='System',
                last_name='Admin',
                role=User.Role.ADMIN
            )
            print("Auto-created admin superuser: admin / admin123")
        else:
            if not admin_user.is_staff or not admin_user.is_superuser:
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save()

        # 2. Demo Doctor Profile
        doc_user, doc_created = User.objects.get_or_create(
            username='dr_smith',
            defaults={
                'email': 'smith@hospital.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': User.Role.DOCTOR
            }
        )
        if doc_created:
            doc_user.set_password('doctor123')
            doc_user.save()

        DoctorProfile.objects.get_or_create(
            user=doc_user,
            defaults={
                'specialization': 'Cardiology',
                'phone': '+1234567890',
                'qualification': 'MBBS, MD (Cardiology)',
                'experience': 10,
                'consultation_fee': 750.00,
                'available_days': 'Monday to Friday'
            }
        )

        # 3. Ensure DoctorProfile exists for ALL DOCTOR role users
        for d_user in User.objects.filter(role=User.Role.DOCTOR):
            DoctorProfile.objects.get_or_create(user=d_user)

        # 4. Ensure PatientProfile exists for ALL PATIENT role users
        for p_user in User.objects.filter(role=User.Role.PATIENT):
            PatientProfile.objects.get_or_create(user=p_user)

        # 5. Demo Patient User (john_doe / patient123)
        patient_user, p_created = User.objects.get_or_create(
            username='john_doe',
            defaults={
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': User.Role.PATIENT
            }
        )
        if p_created:
            patient_user.set_password('patient123')
            patient_user.save()

        from datetime import date, time
        PatientProfile.objects.get_or_create(
            user=patient_user,
            defaults={
                'date_of_birth': date(1990, 5, 15),
                'gender': 'Male',
                'phone': '+9876543210',
                'address': '123 Main Street, NY',
                'blood_group': 'O+'
            }
        )

        # 6. Ensure sample Appointment, Bill, MedicalRecord & Prescription exist for ALL patients
        doc_prof = DoctorProfile.objects.filter(user=doc_user).first() or DoctorProfile.objects.first()
        if doc_prof:
            from hospital.models import Appointment, Bill, MedicalRecord, Prescription
            for pat in PatientProfile.objects.all():
                if not Appointment.objects.filter(patient=pat).exists():
                    app, _ = Appointment.objects.get_or_create(
                        patient=pat,
                        doctor=doc_prof,
                        appointment_date=date.today(),
                        appointment_time=time(10, 0),
                        defaults={
                            'reason': 'General Health & Routine Checkup',
                            'status': Appointment.Status.BOOKED
                        }
                    )
                    Bill.objects.get_or_create(
                        patient=pat,
                        doctor=doc_prof,
                        appointment=app,
                        defaults={
                            'consultation_fee': doc_prof.consultation_fee,
                            'amount': doc_prof.consultation_fee,
                            'status': Bill.Status.PENDING
                        }
                    )
                    MedicalRecord.objects.get_or_create(
                        patient=pat,
                        doctor=doc_prof,
                        appointment=app,
                        defaults={
                            'diagnosis': 'General Health Evaluation - Normal Vitals',
                            'doctor_notes': 'Patient advised balanced diet and regular exercise.'
                        }
                    )
                    Prescription.objects.get_or_create(
                        patient=pat,
                        doctor=doc_prof,
                        appointment=app,
                        medicine_name='Multivitamin Tabs 500mg',
                        defaults={
                            'dosage': 'Once daily after meal',
                            'duration': '15 days',
                            'instructions': 'Take with water.'
                        }
                    )

    except Exception as e:
        print("post_migrate setup note:", e)




class HospitalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hospital'

    def ready(self):
        post_migrate.connect(create_default_admin, sender=self)


