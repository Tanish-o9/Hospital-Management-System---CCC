from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RootApiView,
    RegisterView,
    CustomTokenObtainPairView,
    MeView,
    DoctorListView,
    DoctorDetailView,
    DoctorMyProfileView,
    PatientListView,
    PatientDetailView,
    PatientMyProfileView,
    AppointmentListCreateView,
    AppointmentDetailView,
    MedicalRecordListCreateView,
    MedicalRecordDetailView,
    PrescriptionListCreateView,
    PrescriptionDetailView,
    BillListCreateView,
    BillDetailView,
    DoctorDashboardView,
    PatientDashboardView,
    AdminDashboardView
)

urlpatterns = [
    # Root Welcome Endpoint
    path('', RootApiView.as_view(), name='root-api'),

    # 1. Authentication
    path('api/auth/register/', RegisterView.as_view(), name='auth-register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('api/auth/me/', MeView.as_view(), name='auth-me'),

    # 2. Doctors
    path('api/doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('api/doctors/my-profile/', DoctorMyProfileView.as_view(), name='doctor-my-profile'),
    path('api/doctors/profile/', DoctorMyProfileView.as_view(), name='doctor-profile-action'),
    path('api/doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),

    # 3. Patients
    path('api/patients/', PatientListView.as_view(), name='patient-list'),
    path('api/patients/my-profile/', PatientMyProfileView.as_view(), name='patient-my-profile'),
    path('api/patients/profile/', PatientMyProfileView.as_view(), name='patient-profile-action'),
    path('api/patients/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),

    # 4. Appointments
    path('api/appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('api/appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),

    # 5. Medical Records
    path('api/medical-records/', MedicalRecordListCreateView.as_view(), name='medical-record-list-create'),
    path('api/medical-records/<int:pk>/', MedicalRecordDetailView.as_view(), name='medical-record-detail'),

    # 6. Prescriptions
    path('api/prescriptions/', PrescriptionListCreateView.as_view(), name='prescription-list-create'),
    path('api/prescriptions/<int:pk>/', PrescriptionDetailView.as_view(), name='prescription-detail'),

    # 7. Bills
    path('api/bills/', BillListCreateView.as_view(), name='bill-list-create'),
    path('api/bills/<int:pk>/', BillDetailView.as_view(), name='bill-detail'),

    # 8. Dashboards
    path('api/dashboard/doctor/', DoctorDashboardView.as_view(), name='dashboard-doctor'),
    path('api/dashboard/patient/', PatientDashboardView.as_view(), name='dashboard-patient'),
    path('api/dashboard/admin/', AdminDashboardView.as_view(), name='dashboard-admin'),
]
