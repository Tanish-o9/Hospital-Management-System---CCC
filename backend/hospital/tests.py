from datetime import date, time
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import OTPVerification, DoctorProfile, PatientProfile, Appointment, Bill, MedicalRecord, Prescription

User = get_user_model()


class HospitalManagementTests(APITestCase):

    def setUp(self):
        # Admin User
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='password123',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True
        )

        # Doctor User & Profile
        self.doctor_user = User.objects.create_user(
            username='doc_test',
            email='doc@test.com',
            password='password123',
            role=User.Role.DOCTOR
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='Cardiology',
            consultation_fee=600.00
        )

        # Patient User & Profile
        self.patient_user = User.objects.create_user(
            username='patient_test',
            email='patient@test.com',
            password='password123',
            role=User.Role.PATIENT
        )
        self.patient_profile = PatientProfile.objects.create(
            user=self.patient_user,
            date_of_birth=date(1995, 1, 1),
            gender='Male'
        )

    def test_user_registration(self):
        url = reverse('auth-register')
        data = {
            'username': 'new_patient',
            'email': 'new_patient@test.com',
            'password': 'password123',
            'role': 'PATIENT',
            'date_of_birth': '1998-08-20'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='new_patient').exists())
        patient_profile = PatientProfile.objects.get(user__username='new_patient')
        self.assertEqual(str(patient_profile.date_of_birth), '1998-08-20')

    def test_user_registration_with_dob_alias(self):
        url = reverse('auth-register')
        data = {
            'username': 'new_patient_dob',
            'email': 'new_patient_dob@test.com',
            'password': 'password123',
            'role': 'PATIENT',
            'dob': '2000-05-15'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        patient_profile = PatientProfile.objects.get(user__username='new_patient_dob')
        self.assertEqual(str(patient_profile.date_of_birth), '2000-05-15')

    def test_doctor_registration_with_profile(self):
        url = reverse('auth-register')
        data = {
            'username': 'new_doc',
            'email': 'new_doc@test.com',
            'password': 'password123',
            'role': 'DOCTOR',
            'specialization': 'Neurology',
            'qualification': 'MD, DM',
            'experience': 8,
            'consultation_fee': 850.00
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        doc_profile = DoctorProfile.objects.get(user__username='new_doc')
        self.assertEqual(doc_profile.specialization, 'Neurology')
        self.assertEqual(doc_profile.qualification, 'MD, DM')
        self.assertEqual(doc_profile.experience, 8)
        self.assertEqual(float(doc_profile.consultation_fee), 850.00)

    def test_login_and_jwt_token(self):
        url = reverse('auth-login')
        data = {
            'username': 'doc_test',
            'password': 'password123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)

    def test_appointment_creation_and_auto_billing(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-list-create')
        data = {
            'doctor_id': self.doctor_profile.id,
            'appointment_date': '2026-10-10',
            'appointment_time': '10:00:00',
            'reason': 'Regular Checkup'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify Bill created automatically
        bill = Bill.objects.get(appointment_id=response.data['id'])
        self.assertEqual(bill.amount, self.doctor_profile.consultation_fee)
        self.assertEqual(bill.status, Bill.Status.PENDING)

    def test_duplicate_appointment_prevention(self):
        Appointment.objects.create(
            patient=self.patient_profile,
            doctor=self.doctor_profile,
            appointment_date=date(2026, 10, 10),
            appointment_time=time(10, 0),
            reason='First booking',
            status=Appointment.Status.BOOKED
        )

        self.client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-list-create')
        data = {
            'doctor_id': self.doctor_profile.id,
            'appointment_date': '2026-10-10',
            'appointment_time': '10:00:00',
            'reason': 'Second booking'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Doctor is already booked', str(response.data))

    def test_dashboards(self):
        # Test Doctor Dashboard
        self.client.force_authenticate(user=self.doctor_user)
        res_doc = self.client.get(reverse('dashboard-doctor'))
        self.assertEqual(res_doc.status_code, status.HTTP_200_OK)

        # Test Patient Dashboard
        self.client.force_authenticate(user=self.patient_user)
        res_pat = self.client.get(reverse('dashboard-patient'))
        self.assertEqual(res_pat.status_code, status.HTTP_200_OK)

        # Test Admin Dashboard
        self.client.force_authenticate(user=self.admin_user)
        res_adm = self.client.get(reverse('dashboard-admin'))
        self.assertEqual(res_adm.status_code, status.HTTP_200_OK)

    def test_send_and_verify_otp(self):
        send_url = reverse('auth-send-otp')
        data = {'email': 'otp_test@example.com'}
        response = self.client.post(send_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        otp_record = OTPVerification.objects.get(email='otp_test@example.com')
        otp_code = otp_record.otp_code

        verify_url = reverse('auth-verify-otp')
        verify_data = {'email': 'otp_test@example.com', 'otp': otp_code}
        verify_response = self.client.post(verify_url, verify_data)
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertTrue(verify_response.data['is_verified'])

    def test_predict_disease_endpoint(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('predict-disease')
        data = {'symptoms': 'Fever, cough, chest pain'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('prediction', response.data)
        self.assertIn('medical_record_id', response.data)
