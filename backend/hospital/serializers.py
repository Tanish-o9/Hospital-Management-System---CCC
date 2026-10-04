from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    DoctorProfile,
    PatientProfile,
    Appointment,
    MedicalRecord,
    Prescription,
    Bill
)

User = get_user_model()


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')
        read_only_fields = ('id',)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    otp = serializers.CharField(required=False, allow_blank=True, write_only=True)
    # Patient fields
    date_of_birth = serializers.DateField(required=False, allow_null=True, write_only=True)
    dob = serializers.DateField(required=False, allow_null=True, write_only=True)
    # Doctor fields
    specialization = serializers.CharField(required=False, allow_blank=True, write_only=True)
    phone = serializers.CharField(required=False, allow_blank=True, write_only=True)
    qualification = serializers.CharField(required=False, allow_blank=True, write_only=True)
    experience = serializers.IntegerField(required=False, write_only=True)
    consultation_fee = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
    available_days = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'otp', 'first_name', 'last_name', 'role',
            'date_of_birth', 'dob',
            'specialization', 'phone', 'qualification', 'experience', 'consultation_fee', 'available_days'
        )
        read_only_fields = ('id',)


    def validate_role(self, value):
        if value not in [User.Role.DOCTOR, User.Role.PATIENT, User.Role.ADMIN]:
            raise serializers.ValidationError("Invalid role.")
        return value

    def validate(self, attrs):
        dob = attrs.pop('dob', None)
        if dob and not attrs.get('date_of_birth'):
            attrs['date_of_birth'] = dob
        return super().validate(attrs)

    def create(self, validated_data):
        date_of_birth = validated_data.pop('date_of_birth', None)
        specialization = validated_data.pop('specialization', None)
        phone = validated_data.pop('phone', None)
        qualification = validated_data.pop('qualification', None)
        experience = validated_data.pop('experience', None)
        consultation_fee = validated_data.pop('consultation_fee', None)
        available_days = validated_data.pop('available_days', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', User.Role.PATIENT)
        )

        if user.role == User.Role.PATIENT:
            PatientProfile.objects.get_or_create(
                user=user,
                defaults={'date_of_birth': date_of_birth} if date_of_birth else {}
            )
        elif user.role == User.Role.DOCTOR:
            doc_defaults = {}
            if specialization is not None:
                doc_defaults['specialization'] = specialization
            if phone is not None:
                doc_defaults['phone'] = phone
            if qualification is not None:
                doc_defaults['qualification'] = qualification
            if experience is not None:
                doc_defaults['experience'] = experience
            if consultation_fee is not None:
                doc_defaults['consultation_fee'] = consultation_fee
            if available_days is not None:
                doc_defaults['available_days'] = available_days

            DoctorProfile.objects.get_or_create(
                user=user,
                defaults=doc_defaults
            )
        return user




class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = (
            'id',
            'user',
            'specialization',
            'phone',
            'qualification',
            'experience',
            'consultation_fee',
            'available_days',
            'available_from',
            'available_to'
        )


class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PatientProfile
        fields = (
            'id',
            'user',
            'date_of_birth',
            'gender',
            'phone',
            'address',
            'blood_group',
            'allergies',
            'emergency_contact'
        )


class AppointmentSerializer(serializers.ModelSerializer):
    patient_detail = PatientProfileSerializer(source='patient', read_only=True)
    doctor_detail = DoctorProfileSerializer(source='doctor', read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.all(),
        source='doctor',
        write_only=True
    )
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=PatientProfile.objects.all(),
        source='patient',
        write_only=True,
        required=False
    )

    class Meta:
        model = Appointment
        fields = (
            'id',
            'patient',
            'patient_id',
            'patient_detail',
            'doctor',
            'doctor_id',
            'doctor_detail',
            'appointment_date',
            'appointment_time',
            'reason',
            'status',
            'created_at'
        )
        read_only_fields = ('id', 'patient', 'doctor', 'created_at')

    def validate(self, attrs):
        doctor = attrs.get('doctor')
        appointment_date = attrs.get('appointment_date')
        appointment_time = attrs.get('appointment_time')

        if doctor and appointment_date and appointment_time:
            qs = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status=Appointment.Status.BOOKED
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise serializers.ValidationError("Doctor is already booked at this date and time.")
        return attrs


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_detail = PatientProfileSerializer(source='patient', read_only=True)
    doctor_detail = DoctorProfileSerializer(source='doctor', read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=PatientProfile.objects.all(),
        source='patient',
        write_only=True
    )
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(),
        source='appointment',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = MedicalRecord
        fields = (
            'id',
            'patient',
            'patient_id',
            'patient_detail',
            'doctor',
            'doctor_detail',
            'appointment',
            'appointment_id',
            'diagnosis',
            'doctor_notes',
            'report_file',
            'created_at'
        )
        read_only_fields = ('id', 'patient', 'doctor', 'created_at')


class PredictDiseaseSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(required=False, allow_null=True)
    symptoms = serializers.CharField(required=False, allow_blank=True)
    report_file = serializers.FileField(required=False, allow_null=True)


class PrescriptionSerializer(serializers.ModelSerializer):
    patient_detail = PatientProfileSerializer(source='patient', read_only=True)
    doctor_detail = DoctorProfileSerializer(source='doctor', read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=PatientProfile.objects.all(),
        source='patient',
        write_only=True
    )
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(),
        source='appointment',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Prescription
        fields = (
            'id',
            'patient',
            'patient_id',
            'patient_detail',
            'doctor',
            'doctor_detail',
            'appointment',
            'appointment_id',
            'medicine_name',
            'dosage',
            'duration',
            'instructions',
            'created_at'
        )
        read_only_fields = ('id', 'patient', 'doctor', 'created_at')


class BillSerializer(serializers.ModelSerializer):
    patient_detail = PatientProfileSerializer(source='patient', read_only=True)
    doctor_detail = DoctorProfileSerializer(source='doctor', read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=PatientProfile.objects.all(),
        source='patient',
        write_only=True
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.all(),
        source='doctor',
        write_only=True
    )
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(),
        source='appointment',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Bill
        fields = (
            'id',
            'patient',
            'patient_id',
            'patient_detail',
            'doctor',
            'doctor_id',
            'doctor_detail',
            'appointment',
            'appointment_id',
            'consultation_fee',
            'amount',
            'status',
            'created_at'
        )
        read_only_fields = ('id', 'patient', 'doctor', 'created_at')
