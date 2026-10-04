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

    except Exception as e:
        print("post_migrate setup note:", e)



class HospitalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hospital'

    def ready(self):
        post_migrate.connect(create_default_admin, sender=self)


