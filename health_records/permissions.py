from rest_framework import permissions

class IsPatientOwnerOrAssignedDoctor(permissions.BasePermission):
    """
    Permission to allow patients to access their own records
    and doctors to access records of their assigned patients.
    """
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Patient can access their own records
        if user.user_type == 'PATIENT':
            return obj.patient.user == user
        
        # Doctor can access records of assigned patients
        if user.user_type == 'DOCTOR':
            doctor_profile = user.doctorprofile
            return obj.patient.assigned_doctor == doctor_profile
        
        return False

class IsPatientOwner(permissions.BasePermission):
    """
    Permission to allow only patients to create/update their own records.
    """
    
    def has_permission(self, request, view):
        return request.user.user_type == 'PATIENT'

class IsDoctorAssignedToPatient(permissions.BasePermission):
    """
    Permission for doctors to comment on records of their assigned patients.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'DOCTOR':
            doctor_profile = request.user.doctorprofile
            return obj.patient.assigned_doctor == doctor_profile
        return False
