from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from accounts.models import PatientProfile, DoctorProfile
from .models import HealthRecord, DoctorComment
from .serializers import (
    HealthRecordSerializer, 
    HealthRecordCreateSerializer,
    DoctorCommentSerializer
)
from .permissions import (
    IsPatientOwnerOrAssignedDoctor,
    IsPatientOwner,
    IsDoctorAssignedToPatient
)

class HealthRecordListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HealthRecordCreateSerializer
        return HealthRecordSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'PATIENT':
            patient_profile = get_object_or_404(PatientProfile, user=user)
            return HealthRecord.objects.filter(patient=patient_profile)
        
        elif user.user_type == 'DOCTOR':
            doctor_profile = get_object_or_404(DoctorProfile, user=user)
            return HealthRecord.objects.filter(patient__assigned_doctor=doctor_profile)
        
        return HealthRecord.objects.none()
    
    def perform_create(self, serializer):
        # Only patients can create records
        if self.request.user.user_type != 'PATIENT':
            return Response(
                {'error': 'Only patients can create health records'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        patient_profile = get_object_or_404(PatientProfile, user=self.request.user)
        serializer.save(
            patient=patient_profile,
            created_by=self.request.user
        )

class HealthRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOwnerOrAssignedDoctor]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return HealthRecordCreateSerializer
        return HealthRecordSerializer
    
    def update(self, request, *args, **kwargs):
        # Only patients can update their own records
        if request.user.user_type != 'PATIENT':
            return Response(
                {'error': 'Only patients can update their health records'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        # Only patients can delete their own records
        if request.user.user_type != 'PATIENT':
            return Response(
                {'error': 'Only patients can delete their health records'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_doctor_comment(request, record_id):
    if request.user.user_type != 'DOCTOR':
        return Response(
            {'error': 'Only doctors can add comments'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    health_record = get_object_or_404(HealthRecord, id=record_id)
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    
    # Check if doctor is assigned to this patient
    if health_record.patient.assigned_doctor != doctor_profile:
        return Response(
            {'error': 'You can only comment on records of your assigned patients'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = DoctorCommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(
            health_record=health_record,
            doctor=doctor_profile
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_patients(request):
    """List all patients assigned to the current doctor"""
    if request.user.user_type != 'DOCTOR':
        return Response(
            {'error': 'Only doctors can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    patients = PatientProfile.objects.filter(assigned_doctor=doctor_profile)
    
    data = []
    for patient in patients:
        data.append({
            'id': patient.id,
            'name': patient.user.get_full_name(),
            'email': patient.user.email,
            'phone': patient.user.phone_number,
            'blood_type': patient.blood_type,
            'total_records': patient.health_records.count(),
            'last_visit': patient.health_records.first().visit_date if patient.health_records.exists() else None
        })
    
    return Response(data)
