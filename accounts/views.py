from rest_framework import status, generics, permissions, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, DoctorProfile, PatientProfile
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer,
    DoctorProfileSerializer,
    PatientProfileSerializer
)

class TokenResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    tokens = serializers.DictField(child=serializers.CharField())

class AssignmentResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    patient = PatientProfileSerializer()

@swagger_auto_schema(
    method='post',
    operation_summary="Register User",
    operation_description="Register a new user account (Patient or Doctor)",
    tags=['Authentication'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'email', 'password', 'password_confirm', 'user_type'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Unique username', example='patient1'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email', example='patient@example.com'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password (minimum 8 characters)', example='securepass123'),
            'password_confirm': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm password', example='securepass123'),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name', example='John'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name', example='Doe'),
            'user_type': openapi.Schema(
                type=openapi.TYPE_STRING, 
                enum=['PATIENT', 'DOCTOR'], 
                description='User role type',
                example='PATIENT'
            ),
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number', example='+1234567890'),
            'date_of_birth': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Date of birth', example='1990-01-01'),
        }
    ),
    responses={
    201: TokenResponseSerializer,
    400: openapi.Response(description="Bad Request - Validation errors")
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="User Login",
    operation_description="Login with username and password to get JWT tokens",
    tags=['Authentication'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username', example='patient1'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password', example='securepass123'),
        }
    ),
    responses={
        200: TokenResponseSerializer,
        401: openapi.Response(description="Invalid credentials")
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    return Response(
        {'error': 'Invalid credentials'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Get User Profile",
        operation_description="Get current authenticated user's profile information",
        tags=['User Profile'],
        responses={
            200: PatientProfileSerializer,
            401: openapi.Response(description="Authentication required")
        }
    )
    
    def get_serializer_class(self):
        if self.request.user.user_type == 'DOCTOR':
            return DoctorProfileSerializer
        return PatientProfileSerializer
    
    def get_object(self):
        if self.request.user.user_type == 'DOCTOR':
            return DoctorProfile.objects.get(user=self.request.user)
        return PatientProfile.objects.get(user=self.request.user)

@swagger_auto_schema(
    method='post',
    operation_summary="Assign Doctor to Patient",
    operation_description="Assign a doctor to a patient (Doctor or Admin only)",
    tags=['Doctor Management'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['patient_id'],
        properties={
            'patient_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Patient ID to assign', example=1),
            'doctor_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Doctor ID (optional, defaults to current user)', example=1),
        }
    ),
    responses={
        200:AssignmentResponseSerializer,
        403: openapi.Response(description="Only doctors or admin can assign doctors"),
        404: openapi.Response(description="Patient or doctor not found")
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_doctor_to_patient(request):
    """Admin or doctor can assign themselves to a patient"""
    if request.user.user_type != 'DOCTOR' and not request.user.is_staff:
        return Response(
            {'error': 'Only doctors or admin can assign doctors to patients'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    patient_id = request.data.get('patient_id')
    doctor_id = request.data.get('doctor_id', request.user.doctorprofile.id if hasattr(request.user, 'doctorprofile') else None)
    
    try:
        patient = PatientProfile.objects.get(id=patient_id)
        doctor = DoctorProfile.objects.get(id=doctor_id)
        
        # Update assignment
        old_doctor = patient.assigned_doctor
        patient.assigned_doctor = doctor
        patient.save()
        
        # Send notification to new doctor
        if old_doctor != doctor:
            from notifications.tasks import send_patient_assignment_notification
            send_patient_assignment_notification.delay(
                doctor.user.id,
                patient.user.get_full_name()
            )
        
        return Response({
            'message': f'Patient {patient.user.get_full_name()} assigned to Dr. {doctor.user.get_full_name()}',
            'patient': PatientProfileSerializer(patient).data
        })
        
    except (PatientProfile.DoesNotExist, DoctorProfile.DoesNotExist) as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )

@swagger_auto_schema(
    method='get',
    operation_summary="List Available Doctors",
    operation_description="Get list of all available doctors for assignment",
    tags=['Doctor Management'],
    responses={
        200: DoctorProfileSerializer(many=True),
        401: openapi.Response(description="Authentication required")
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def available_doctors(request):
    """List all available doctors for assignment"""
    doctors = DoctorProfile.objects.all()
    return Response(DoctorProfileSerializer(doctors, many=True).data)
