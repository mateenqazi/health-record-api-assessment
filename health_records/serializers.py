from rest_framework import serializers
from .models import HealthRecord, DoctorComment
from accounts.serializers import UserSerializer, DoctorProfileSerializer

class DoctorCommentSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileSerializer(read_only=True)
    
    class Meta:
        model = DoctorComment
        fields = ['id', 'comment', 'is_private', 'created_at', 'updated_at', 'doctor']  # Remove health_record
        read_only_fields = ['doctor', 'created_at', 'updated_at']

class HealthRecordSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    doctor_comments = serializers.SerializerMethodField()
    
    class Meta:
        model = HealthRecord
        fields = '__all__'
        read_only_fields = ['patient', 'created_by', 'created_at', 'updated_at']
    
    def get_doctor_comments(self, obj):
        user = self.context['request'].user
        comments = obj.doctor_comments.all()
        
        # If user is a patient, exclude private comments
        if user.user_type == 'PATIENT':
            comments = comments.filter(is_private=False)
        
        return DoctorCommentSerializer(comments, many=True).data

class HealthRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = [
            'record_type', 'title', 'description', 'symptoms',
            'diagnosis', 'treatment', 'medications', 'visit_date'
        ]
