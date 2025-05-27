from django.contrib import admin
from .models import HealthRecord, DoctorComment

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'title', 'record_type', 'visit_date', 'created_at']
    list_filter = ['record_type', 'visit_date', 'created_at']
    search_fields = ['patient__user__username', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(DoctorComment)
class DoctorCommentAdmin(admin.ModelAdmin):
    list_display = ['health_record', 'doctor', 'is_private', 'created_at']
    list_filter = ['is_private', 'created_at']
    search_fields = ['health_record__title', 'doctor__user__username']
