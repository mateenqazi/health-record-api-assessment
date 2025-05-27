
from rest_framework import serializers

from django.contrib.auth import authenticate

from .models import User, DoctorProfile, PatientProfile

class UserRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, min_length=8)

    password_confirm = serializers.CharField(write_only=True)

    

    class Meta:

        model = User

        fields = [

            'username', 'email', 'password', 'password_confirm',

            'first_name', 'last_name', 'user_type', 'phone_number', 

            'date_of_birth'

        ]

    

    def validate(self, attrs):

        if attrs['password'] != attrs['password_confirm']:

            raise serializers.ValidationError("Passwords don't match")

        return attrs

    

    def create(self, validated_data):

        validated_data.pop('password_confirm')

        password = validated_data.pop('password')

        user = User.objects.create_user(**validated_data)

        user.set_password(password)

        user.save()

        

        # Create profile based on user type

        if user.user_type == 'DOCTOR':

            DoctorProfile.objects.create(

                user=user,

                specialization='General',

                license_number=f'DOC{user.id:06d}',

                years_of_experience=0

            )

        else:

            PatientProfile.objects.create(

                user=user,

                emergency_contact='',

                blood_type='',

                allergies=''

            )

        

        return user

class UserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User

        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type']

class DoctorProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    

    class Meta:

        model = DoctorProfile

        fields = '__all__'

class PatientProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    assigned_doctor = DoctorProfileSerializer(read_only=True)

    

    class Meta:

        model = PatientProfile

        fields = '__all__'

