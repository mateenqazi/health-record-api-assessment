from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import User, DoctorProfile, PatientProfile
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer,
    DoctorProfileSerializer,
    PatientProfileSerializer
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
    
    def get_serializer_class(self):
        if self.request.user.user_type == 'DOCTOR':
            return DoctorProfileSerializer
        return PatientProfileSerializer
    
    def get_object(self):
        if self.request.user.user_type == 'DOCTOR':
            return DoctorProfile.objects.get(user=self.request.user)
        return PatientProfile.objects.get(user=self.request.user)

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

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def available_doctors(request):
    """List all available doctors for assignment"""
    doctors = DoctorProfile.objects.all()
    return Response(DoctorProfileSerializer(doctors, many=True).data)
