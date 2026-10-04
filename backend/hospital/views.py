from django.utils import timezone
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, parsers
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

import random
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    OTPVerification,
    User,
    DoctorProfile,
    PatientProfile,
    Appointment,
    MedicalRecord,
    Prescription,
    Bill
)

from .serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    PredictDiseaseSerializer,
    UserSerializer,
    RegisterSerializer,
    DoctorProfileSerializer,
    PatientProfileSerializer,
    AppointmentSerializer,
    MedicalRecordSerializer,
    PrescriptionSerializer,
    BillSerializer
)

from .permissions import IsDoctor, IsPatient, IsAdmin


# ==================================================
# 1. AUTHENTICATION & OTP VIEWS
# ==================================================

class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = f"{random.randint(100000, 999999)}"
            
            OTPVerification.objects.update_or_create(
                email=email,
                defaults={
                    'otp_code': otp_code,
                    'is_verified': False,
                    'created_at': timezone.now()
                }
            )

            subject = "Your Hospital System OTP Code"
            message = f"Hello,\n\nYour 6-digit OTP verification code is: {otp_code}\nThis OTP is valid for 10 minutes.\n\nThank you!"
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hospital.com')
            
            try:
                send_mail(subject, message, from_email, [email], fail_silently=True)
            except Exception:
                pass

            return Response(
                {
                    "message": "OTP sent successfully to email.",
                    "email": email
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            try:
                record = OTPVerification.objects.get(email=email)
            except OTPVerification.DoesNotExist:
                return Response({"error": "No OTP request found for this email."}, status=status.HTTP_404_NOT_FOUND)

            if record.is_expired():
                return Response({"error": "OTP has expired. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)

            if record.otp_code != otp:
                return Response({"error": "Invalid OTP code."}, status=status.HTTP_400_BAD_REQUEST)

            record.is_verified = True
            record.save()

            return Response({"message": "OTP verified successfully.", "email": email, "is_verified": True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            provided_otp = request.data.get('otp') or serializer.validated_data.get('otp')

            otp_record = OTPVerification.objects.filter(email=email).first()

            if provided_otp:
                if not otp_record or otp_record.otp_code != provided_otp:
                    return Response({"error": "Invalid OTP code provided for registration."}, status=status.HTTP_400_BAD_REQUEST)
                if otp_record.is_expired():
                    return Response({"error": "OTP has expired. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)
                otp_record.is_verified = True
                otp_record.save()
            elif otp_record:
                if not otp_record.is_verified:
                    return Response(
                        {"error": "Email OTP was requested but not verified yet. Please verify OTP before creating an account."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if otp_record.is_expired():
                    return Response({"error": "OTP verification expired. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            
            # Cleanup OTP verification record after successful account creation
            if otp_record:
                otp_record.delete()

            user_data = UserSerializer(user).data
            if hasattr(user, 'patient_profile') and user.patient_profile:
                user_data['patient_profile'] = PatientProfileSerializer(user.patient_profile).data
            elif hasattr(user, 'doctor_profile') and user.doctor_profile:
                user_data['doctor_profile'] = DoctorProfileSerializer(user.doctor_profile).data

            return Response(
                {
                    "message": "User registered successfully.",
                    "user": user_data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==================================================
# 2. DOCTOR MANAGEMENT VIEWS
# ==================================================

class DoctorListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        doctors = DoctorProfile.objects.select_related('user').all()
        serializer = DoctorProfileSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DoctorDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            doctor = DoctorProfile.objects.select_related('user').get(pk=pk)
        except DoctorProfile.DoesNotExist:
            return Response({"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DoctorProfileSerializer(doctor)
        return Response(serializer.data, status=status.HTTP_200_OK)



class DoctorMyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def get(self, request):
        profile, _ = DoctorProfile.objects.get_or_create(user=request.user)
        serializer = DoctorProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if hasattr(request.user, 'doctor_profile'):
            return Response({"error": "Doctor profile already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = DoctorProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            profile = request.user.doctor_profile
        except DoctorProfile.DoesNotExist:
            profile = DoctorProfile.objects.create(user=request.user)
        
        # Also update User fields if passed
        user = request.user
        updated_user = False
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
            updated_user = True
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
            updated_user = True
        if 'email' in request.data:
            user.email = request.data['email']
            updated_user = True
        if updated_user:
            user.save()

        serializer = DoctorProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================================================
# 3. PATIENT MANAGEMENT VIEWS
# ==================================================

class PatientListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role in [User.Role.ADMIN, User.Role.DOCTOR] or request.user.is_superuser:
            patients = PatientProfile.objects.select_related('user').all()
            serializer = PatientProfileSerializer(patients, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


class PatientDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            patient = PatientProfile.objects.select_related('user').get(pk=pk)
        except PatientProfile.DoesNotExist:
            return Response({"error": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user.role in [User.Role.ADMIN, User.Role.DOCTOR] or request.user.is_superuser or patient.user == request.user:
            serializer = PatientProfileSerializer(patient)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


class PatientMyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    def get(self, request):
        profile, _ = PatientProfile.objects.get_or_create(user=request.user)
        serializer = PatientProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if hasattr(request.user, 'patient_profile'):
            return Response({"error": "Patient profile already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PatientProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            profile = request.user.patient_profile
        except PatientProfile.DoesNotExist:
            profile = PatientProfile.objects.create(user=request.user)
        
        # Also update User fields if passed
        user = request.user
        updated_user = False
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
            updated_user = True
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
            updated_user = True
        if 'email' in request.data:
            user.email = request.data['email']
            updated_user = True
        if updated_user:
            user.save()

        serializer = PatientProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================================================
# 4. APPOINTMENT VIEWS
# ==================================================

class AppointmentListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = Appointment.objects.select_related('patient__user', 'doctor__user').all()

        if user.role == User.Role.PATIENT:
            queryset = queryset.filter(patient__user=user)
        elif user.role == User.Role.DOCTOR:
            queryset = queryset.filter(doctor__user=user)
        elif not (user.role == User.Role.ADMIN or user.is_superuser):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param.upper())

        upcoming = request.query_params.get('upcoming')
        if upcoming and upcoming.lower() in ['true', '1']:
            queryset = queryset.filter(
                appointment_date__gte=timezone.now().date(),
                status=Appointment.Status.BOOKED
            )

        serializer = AppointmentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        if user.role == User.Role.PATIENT:
            patient_profile, _ = PatientProfile.objects.get_or_create(user=user)
        elif user.role in [User.Role.ADMIN, User.Role.DOCTOR] or user.is_superuser:
            patient_id = request.data.get('patient_id')
            if not patient_id:
                return Response({"error": "patient_id is required for non-patient booking."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                patient_profile = PatientProfile.objects.get(pk=patient_id)
            except PatientProfile.DoesNotExist:
                return Response({"error": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            appointment = serializer.save(patient=patient_profile)
            
            # Auto-generate bill
            fee = appointment.doctor.consultation_fee
            Bill.objects.create(
                patient=appointment.patient,
                doctor=appointment.doctor,
                appointment=appointment,
                consultation_fee=fee,
                amount=fee,
                status=Bill.Status.PENDING
            )

            return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        try:
            appointment = Appointment.objects.select_related('patient__user', 'doctor__user').get(pk=pk)
            if user.role == User.Role.PATIENT and appointment.patient.user != user:
                return None
            if user.role == User.Role.DOCTOR and appointment.doctor.user != user:
                return None
            return appointment
        except Appointment.DoesNotExist:
            return None

    def get(self, request, pk):
        appointment = self.get_object(pk, request.user)
        if not appointment:
            return Response({"error": "Appointment not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        appointment = self.get_object(pk, request.user)
        if not appointment:
            return Response({"error": "Appointment not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        appointment = self.get_object(pk, request.user)
        if not appointment:
            return Response({"error": "Appointment not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)
        appointment.delete()
        return Response({"message": "Appointment deleted successfully."}, status=status.HTTP_200_OK)


# ==================================================
# 5. MEDICAL RECORD VIEWS
# ==================================================

class MedicalRecordListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = MedicalRecord.objects.select_related('patient__user', 'doctor__user', 'appointment').all()

        if user.role == User.Role.PATIENT:
            queryset = queryset.filter(patient__user=user)
        elif user.role == User.Role.DOCTOR:
            queryset = queryset.filter(doctor__user=user)
        elif not (user.role == User.Role.ADMIN or user.is_superuser):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = MedicalRecordSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        if not (user.role == User.Role.DOCTOR or user.role == User.Role.ADMIN or user.is_superuser):
            return Response({"error": "Only doctors can create medical records."}, status=status.HTTP_403_FORBIDDEN)

        try:
            doctor_profile = user.doctor_profile
        except DoctorProfile.DoesNotExist:
            if user.role == User.Role.ADMIN or user.is_superuser:
                doctor_id = request.data.get('doctor_id')
                if doctor_id:
                    doctor_profile = DoctorProfile.objects.get(pk=doctor_id)
                else:
                    return Response({"error": "doctor_id is required when Admin creates record."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Doctor profile required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MedicalRecordSerializer(data=request.data)
        if serializer.is_valid():
            record = serializer.save(doctor=doctor_profile)
            return Response(MedicalRecordSerializer(record).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MedicalRecordDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        try:
            record = MedicalRecord.objects.select_related('patient__user', 'doctor__user').get(pk=pk)
            if user.role == User.Role.PATIENT and record.patient.user != user:
                return None
            if user.role == User.Role.DOCTOR and record.doctor.user != user:
                return None
            return record
        except MedicalRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        record = self.get_object(pk, request.user)
        if not record:
            return Response({"error": "Medical record not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)
        serializer = MedicalRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if request.user.role not in [User.Role.DOCTOR, User.Role.ADMIN] and not request.user.is_superuser:
            return Response({"error": "Patients cannot update medical records."}, status=status.HTTP_403_FORBIDDEN)
        
        record = self.get_object(pk, request.user)
        if not record:
            return Response({"error": "Medical record not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MedicalRecordSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================================================
# 6. PRESCRIPTION VIEWS
# ==================================================

class PrescriptionListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = Prescription.objects.select_related('patient__user', 'doctor__user', 'appointment').all()

        if user.role == User.Role.PATIENT:
            queryset = queryset.filter(patient__user=user)
        elif user.role == User.Role.DOCTOR:
            queryset = queryset.filter(doctor__user=user)
        elif not (user.role == User.Role.ADMIN or user.is_superuser):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PrescriptionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        if not (user.role == User.Role.DOCTOR or user.role == User.Role.ADMIN or user.is_superuser):
            return Response({"error": "Only doctors can create prescriptions."}, status=status.HTTP_403_FORBIDDEN)

        try:
            doctor_profile = user.doctor_profile
        except DoctorProfile.DoesNotExist:
            if user.role == User.Role.ADMIN or user.is_superuser:
                doctor_id = request.data.get('doctor_id')
                if doctor_id:
                    doctor_profile = DoctorProfile.objects.get(pk=doctor_id)
                else:
                    return Response({"error": "doctor_id is required when Admin creates prescription."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Doctor profile required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PrescriptionSerializer(data=request.data)
        if serializer.is_valid():
            prescription = serializer.save(doctor=doctor_profile)
            return Response(PrescriptionSerializer(prescription).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrescriptionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        try:
            prescription = Prescription.objects.select_related('patient__user', 'doctor__user').get(pk=pk)
            if user.role == User.Role.PATIENT and prescription.patient.user != user:
                return None
            if user.role == User.Role.DOCTOR and prescription.doctor.user != user:
                return None
            return prescription
        except Prescription.DoesNotExist:
            return None

    def get(self, request, pk):
        prescription = self.get_object(pk, request.user)
        if not prescription:
            return Response({"error": "Prescription not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if request.user.role not in [User.Role.DOCTOR, User.Role.ADMIN] and not request.user.is_superuser:
            return Response({"error": "Patients cannot update prescriptions."}, status=status.HTTP_403_FORBIDDEN)

        prescription = self.get_object(pk, request.user)
        if not prescription:
            return Response({"error": "Prescription not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PrescriptionSerializer(prescription, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================================================
# 7. BILLING VIEWS
# ==================================================

class BillListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = Bill.objects.select_related('patient__user', 'doctor__user', 'appointment').all()

        if user.role == User.Role.PATIENT:
            queryset = queryset.filter(patient__user=user)
        elif user.role == User.Role.DOCTOR:
            queryset = queryset.filter(doctor__user=user)
        elif not (user.role == User.Role.ADMIN or user.is_superuser):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = BillSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        if not (user.role in [User.Role.ADMIN, User.Role.DOCTOR] or user.is_superuser):
            return Response({"error": "Only Admins or Doctors can manually generate bills."}, status=status.HTTP_403_FORBIDDEN)

        serializer = BillSerializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.validated_data.get('doctor')
            consultation_fee = serializer.validated_data.get('consultation_fee') or doctor.consultation_fee
            amount = serializer.validated_data.get('amount') or consultation_fee

            bill = serializer.save(consultation_fee=consultation_fee, amount=amount)
            return Response(BillSerializer(bill).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BillDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        try:
            bill = Bill.objects.select_related('patient__user', 'doctor__user').get(pk=pk)
            if user.role == User.Role.PATIENT and bill.patient.user != user:
                return None
            if user.role == User.Role.DOCTOR and bill.doctor.user != user:
                return None
            return bill
        except Bill.DoesNotExist:
            return None

    def get(self, request, pk):
        bill = self.get_object(pk, request.user)
        if not bill:
            return Response({"error": "Bill not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BillSerializer(bill)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        bill = self.get_object(pk, request.user)
        if not bill:
            return Response({"error": "Bill not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BillSerializer(bill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================================================
# 8. DASHBOARD VIEWS
# ==================================================

class DoctorDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def get(self, request):
        doctor_profile, _ = DoctorProfile.objects.get_or_create(user=request.user)

        appointments_qs = Appointment.objects.filter(doctor=doctor_profile)
        
        total_appointments = appointments_qs.count()
        upcoming_appointments = appointments_qs.filter(
            appointment_date__gte=timezone.now().date(),
            status=Appointment.Status.BOOKED
        ).count()
        completed_appointments = appointments_qs.filter(status=Appointment.Status.COMPLETED).count()
        total_patients = appointments_qs.values('patient').distinct().count()
        
        recent_appointments = appointments_qs.select_related('patient__user', 'doctor__user')[:5]

        data = {
            "total_appointments": total_appointments,
            "upcoming_appointments": upcoming_appointments,
            "completed_appointments": completed_appointments,
            "total_patients": total_patients,
            "recent_appointments": AppointmentSerializer(recent_appointments, many=True).data
        }
        return Response(data, status=status.HTTP_200_OK)


class PatientDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    def get(self, request):
        patient_profile, _ = PatientProfile.objects.get_or_create(user=request.user)

        # Auto-seed sample records for patient if they have 0 appointments
        if not Appointment.objects.filter(patient=patient_profile).exists():
            from datetime import timedelta, time
            doc_prof = DoctorProfile.objects.first()
            if doc_prof:
                app = Appointment.objects.create(
                    patient=patient_profile,
                    doctor=doc_prof,
                    appointment_date=timezone.now().date() + timedelta(days=3),
                    appointment_time=time(10, 30),
                    reason='General Health Checkup & Consultation',
                    status=Appointment.Status.BOOKED
                )
                Bill.objects.create(
                    patient=patient_profile,
                    doctor=doc_prof,
                    appointment=app,
                    consultation_fee=doc_prof.consultation_fee,
                    amount=doc_prof.consultation_fee,
                    status=Bill.Status.PENDING
                )
                MedicalRecord.objects.create(
                    patient=patient_profile,
                    doctor=doc_prof,
                    appointment=app,
                    diagnosis='General Wellness Routine Evaluation',
                    doctor_notes='Patient advised regular hydration and daily exercise.'
                )
                Prescription.objects.create(
                    patient=patient_profile,
                    doctor=doc_prof,
                    appointment=app,
                    medicine_name='Multivitamin Supplement 500mg',
                    dosage='Once daily after breakfast',
                    duration='30 days',
                    instructions='Take with water daily.'
                )

        appointments_qs = Appointment.objects.filter(patient=patient_profile)
        prescriptions_qs = Prescription.objects.filter(patient=patient_profile)
        bills_qs = Bill.objects.filter(patient=patient_profile)

        upcoming_appointments = appointments_qs.filter(
            status=Appointment.Status.BOOKED
        ).count()
        appointment_history_count = appointments_qs.count()
        recent_prescriptions = prescriptions_qs.select_related('doctor__user', 'patient__user')[:5]
        pending_bills = bills_qs.filter(status=Bill.Status.PENDING).count()
        total_bills = bills_qs.count()

        data = {
            "upcoming_appointments": upcoming_appointments,
            "appointment_history_count": appointment_history_count,
            "recent_prescriptions": PrescriptionSerializer(recent_prescriptions, many=True).data,
            "pending_bills": pending_bills,
            "total_bills": total_bills
        }
        return Response(data, status=status.HTTP_200_OK)



class AdminDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        total_doctors = DoctorProfile.objects.count()
        total_patients = PatientProfile.objects.count()
        
        total_appointments = Appointment.objects.count()
        completed_appointments = Appointment.objects.filter(status=Appointment.Status.COMPLETED).count()
        pending_appointments = Appointment.objects.filter(status=Appointment.Status.BOOKED).count()

        total_bills = Bill.objects.count()
        pending_bills = Bill.objects.filter(status=Bill.Status.PENDING).count()

        data = {
            "total_doctors": total_doctors,
            "total_patients": total_patients,
            "total_appointments": total_appointments,
            "completed_appointments": completed_appointments,
            "pending_appointments": pending_appointments,
            "total_bills": total_bills,
            "pending_bills": pending_bills
        }
        return Response(data, status=status.HTTP_200_OK)


class RootApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "message": "Hospital Management System API is running successfully!",
            "status": "online",
            "endpoints": {
                "auth_register": "/api/auth/register/",
                "auth_login": "/api/auth/login/",
                "predict_disease": "/api/predict-disease/",
                "doctors": "/api/doctors/",
                "patients": "/api/patients/",
                "appointments": "/api/appointments/",
                "medical_records": "/api/medical-records/",
                "prescriptions": "/api/prescriptions/",
                "bills": "/api/bills/",
                "admin": "/admin/"
            }
        }, status=status.HTTP_200_OK)


# ==================================================
# 9. ML DISEASE PREDICTION VIEW
# ==================================================

class PredictDiseaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser
    ]

    def post(self, request):
        serializer = PredictDiseaseSerializer(data=request.data)
            

                predicted_disease = highest_risk.get(
                    "disease",
                    "Unknown"
                )

                risk_percent = highest_risk.get(
                    "risk_percent",
                    0
                )

                risk_level = highest_risk.get(
                    "risk_level",
                    "Unknown"
                )

                confidence = f"{risk_percent}%"

                recommendation = (
                    f"Risk level: {risk_level}. "
                    "Consult a qualified doctor for "
                    "clinical evaluation."
                )

            else:
                predicted_disease = (
                    "No disease risk detected"
                )
                confidence = "0%"
                recommendation = (
                    "No significant disease risk was "
                    "identified. Consult a doctor if "
                    "symptoms persist."
                )


                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        except Exception as exc:
            return Response(
                {
                    "error": "ML prediction failed.",
                    "details": str(exc)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ==================================================
        # SAVE MEDICAL RECORD
        # ==================================================

        medical_record = None

        if patient_profile:
            assigned_doctor = DoctorProfile.objects.first()

            if assigned_doctor:
                medical_record = MedicalRecord.objects.create(
                    patient=patient_profile,
                    doctor=assigned_doctor,
                    diagnosis=(
                        f"ML Predicted: {predicted_disease} "
                        f"(Confidence: {confidence})"
                    ),
                    doctor_notes=(
                        f"Symptoms: {symptoms}. "
                        f"Recommendation: {recommendation}"
                    ),
                    report_file=report_file
                )

        # ==================================================
        # RESPONSE
        # ==================================================

        file_url = None

        if medical_record and medical_record.report_file:
            file_url = request.build_absolute_uri(
                medical_record.report_file.url
            )

        response_data = {
            "message": "ML Disease prediction completed.",
            "prediction": {
                "disease": predicted_disease,
                "confidence": confidence,
                "recommendation": recommendation
            },
            "medical_record_id": (
                medical_record.id
                if medical_record
                else None
            ),
            "report_file_url": file_url
        }


