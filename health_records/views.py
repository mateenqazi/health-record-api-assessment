from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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
from rest_framework import serializers

from .permissions import (
    IsPatientOwnerOrAssignedDoctor,
    IsPatientOwner,
    IsDoctorAssignedToPatient
)

class PatientSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.CharField()
    phone = serializers.CharField()
    blood_type = serializers.CharField()
    total_records = serializers.IntegerField()
    last_visit = serializers.DateTimeField(allow_null=True)

class HealthRecordListCreateView(generics.ListCreateAPIView):
    """
    Health Records Management
    
    GET: List health records (patients see their own, doctors see assigned patients)
    POST: Create new health record (patients only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="List Health Records",
        operation_description="Get list of health records. Patients see their own records, doctors see records of assigned patients.",
        tags=['Health Records'],
        responses={
            200: HealthRecordSerializer(many=True),
            401: openapi.Response(description="Authentication required")
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Create Health Record",
        operation_description="Create a new health record (patients only)",
        tags=['Health Records'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['record_type', 'title', 'visit_date'],
            properties={
                'record_type': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    enum=['CHECKUP', 'DIAGNOSIS', 'PRESCRIPTION', 'LAB_RESULT', 'EMERGENCY'],
                    description='Type of health record',
                    example='CHECKUP'
                ),
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Record title', example='Annual Physical'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Detailed description', example='Routine annual health checkup'),
                'symptoms': openapi.Schema(type=openapi.TYPE_STRING, description='Patient symptoms', example='No specific symptoms'),
                'diagnosis': openapi.Schema(type=openapi.TYPE_STRING, description='Medical diagnosis', example='Patient appears healthy'),
                'treatment': openapi.Schema(type=openapi.TYPE_STRING, description='Treatment plan', example='Continue current lifestyle'),
                'medications': openapi.Schema(type=openapi.TYPE_STRING, description='Prescribed medications', example='Daily multivitamin'),
                'visit_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Visit date and time', example='2025-05-28T10:00:00Z'),
            }
        ),
        responses={
            201: HealthRecordSerializer,
            403: openapi.Response(description="Only patients can create health records"),
            401: openapi.Response(description="Authentication required"),
            400: openapi.Response(description="Validation errors")
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
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
    """
    Health Record Detail Management
    
    GET: Retrieve specific health record
    PUT/PATCH: Update health record (patients only)
    DELETE: Delete health record (patients only)
    """
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOwnerOrAssignedDoctor]
    
    @swagger_auto_schema(
        operation_summary="Get Health Record",
        operation_description="Retrieve a specific health record by ID",
        tags=['Health Records'],
        responses={
           200: HealthRecordSerializer,
            404: openapi.Response(description="Health record not found"),
            403: openapi.Response(description="Permission denied - not owner or assigned doctor"),
            401: openapi.Response(description="Authentication required")
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Update Health Record",
        operation_description="Update a health record (patients only)",
        tags=['Health Records'],
        responses={
            200: HealthRecordSerializer,
            403: openapi.Response(description="Only patients can update their health records"),
            404: openapi.Response(description="Health record not found"),
            401: openapi.Response(description="Authentication required")
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Delete Health Record",
        operation_description="Delete a health record (patients only)",
        tags=['Health Records'],
        responses={
            204: openapi.Response(description="Health record deleted successfully"),
            403: openapi.Response(description="Only patients can delete their health records"),
            404: openapi.Response(description="Health record not found"),
            401: openapi.Response(description="Authentication required")
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return HealthRecordCreateSerializer
        return HealthRecordSerializer
    
    def update(self, request, *args, **kwargs):
        if request.user.user_type != 'PATIENT':
            return Response(
                {'error': 'Only patients can update their health records'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if request.user.user_type != 'PATIENT':
            return Response(
                {'error': 'Only patients can delete their health records'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

@swagger_auto_schema(
    method='post',
    operation_summary="Add Doctor Comment",
    operation_description="Add a comment to a health record (assigned doctors only)",
    tags=['Health Records'],
    manual_parameters=[
        openapi.Parameter('record_id', openapi.IN_PATH, description="Health record ID", type=openapi.TYPE_INTEGER, required=True)
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['comment'],
        properties={
            'comment': openapi.Schema(type=openapi.TYPE_STRING, description='Doctor comment on the health record', example='Patient shows good health indicators. Recommend annual follow-up.'),
            'is_private': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Private comment visible only to doctors', default=False, example=False),
        }
    ),
    responses={
        201: DoctorCommentSerializer,
        403: openapi.Response(description="Only assigned doctors can comment"),
        404: openapi.Response(description="Health record not found"),
        401: openapi.Response(description="Authentication required")
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_doctor_comment(request, record_id):
    """Add doctor comment to health record"""
    if request.user.user_type != 'DOCTOR':
        return Response(
            {'error': 'Only doctors can add comments'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    health_record = get_object_or_404(HealthRecord, id=record_id)
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    
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

@swagger_auto_schema(
    method='get',
    operation_summary="My Patients",
    operation_description="Get list of patients assigned to the current doctor",
    tags=['Doctor Management'],
    responses={
        200: PatientSummarySerializer(many=True),
        403: openapi.Response(description="Only doctors can access this endpoint"),
        401: openapi.Response(description="Authentication required")
    }
)
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