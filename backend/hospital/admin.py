from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
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


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp_code', 'is_verified', 'created_at')
    search_fields = ('email', 'otp_code')
    list_filter = ('is_verified', 'created_at')


class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = 'Doctor Profile'
    fk_name = 'user'
    extra = 0


class PatientProfileInline(admin.StackedInline):
    model = PatientProfile
    can_delete = False
    verbose_name_plural = 'Patient Profile'
    fk_name = 'user'
    extra = 0


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (DoctorProfileInline, PatientProfileInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )



@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'phone', 'experience', 'consultation_fee')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization')


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender', 'phone', 'blood_group')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('patient__user__username', 'doctor__user__username', 'reason')


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'appointment', 'created_at')
    search_fields = ('patient__user__username', 'doctor__user__username', 'diagnosis')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'medicine_name', 'dosage', 'duration', 'created_at')
    search_fields = ('patient__user__username', 'doctor__user__username', 'medicine_name')


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'consultation_fee', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__user__username', 'doctor__user__username')
