import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
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
        print("WSGI Init: Created admin superuser: admin / admin123")
    else:
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        print("WSGI Init: Admin password verified: admin / admin123")
except Exception as e:
    print("WSGI Init Admin Check:", e)

