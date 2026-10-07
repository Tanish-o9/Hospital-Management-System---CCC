from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone


# 0. OTP Verification Model
class OTPVerification(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def is_expired(self):
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"OTP for {self.email}: {self.otp_code} (Verified: {self.is_verified})"


# 1. Custom User Model
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        DOCTOR = 'DOCTOR', 'Doctor'
        PATIENT = 'PATIENT', 'Patient'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT
    )
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


# 2. Doctor Profile Model
class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    specialization = models.CharField(max_length=100, default='General Physician')
    phone = models.CharField(max_length=20, blank=True)
    qualification = models.CharField(max_length=100, blank=True)
    experience = models.IntegerField(default=0, help_text="Years of experience")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    available_days = models.CharField(max_length=100, default='Monday to Friday')
    available_from = models.TimeField(default='09:00:00')
    available_to = models.TimeField(default='17:00:00')

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.specialization}"


# 3. Patient Profile Model
class PatientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=10, blank=True)
    allergies = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name() or self.user.username}"


# 4. Appointment Model
class Appointment(models.Model):
    class Status(models.TextChoices):
        BOOKED = 'BOOKED', 'Booked'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.BOOKED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']

    def __str__(self):
        return f"Appointment #{self.id}: {self.patient.user.username} with Dr. {self.doctor.user.username}"


# 5. Medical Record Model
class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name='medical_records'
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='medical_records'
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medical_records'
    )
    diagnosis = models.TextField()
    doctor_notes = models.TextField(blank=True)
    report_file = models.FileField(upload_to='medical_reports/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Medical Record for {self.patient.user.username} by Dr. {self.doctor.user.username}"


# 6. Prescription Model
class Prescription(models.Model):
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescriptions'
    )
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription ({self.medicine_name}) for {self.patient.user.username}"


# 7. Bill Model
class Bill(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name='bills'
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='bills'
    )
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bill'
    )
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Bill #{self.id} for {self.patient.user.username} - ${self.amount} ({self.status})"
