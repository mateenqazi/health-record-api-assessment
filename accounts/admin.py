from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DoctorProfile, PatientProfile

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'user_type', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_active', 'date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'date_of_birth')
        }),
    )

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'license_number', 'years_of_experience']
    search_fields = ['user__username', 'user__email', 'specialization']

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'assigned_doctor', 'blood_type', 'emergency_contact']
    list_filter = ['assigned_doctor', 'blood_type']
    search_fields = ['user__username', 'user__email']
    
    def save_model(self, request, obj, form, change):
        # Trigger notification when doctor is assigned
        if change and 'assigned_doctor' in form.changed_data and obj.assigned_doctor:
            from notifications.tasks import send_patient_assignment_notification
            send_patient_assignment_notification.delay(
                obj.assigned_doctor.user.id,
                obj.user.get_full_name()
            )
        super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)
