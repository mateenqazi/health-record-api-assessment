from django.db import models
from accounts.models import User, PatientProfile, DoctorProfile

class HealthRecord(models.Model):
    RECORD_TYPE_CHOICES = [
        ('CHECKUP', 'Regular Checkup'),
        ('DIAGNOSIS', 'Diagnosis'),
        ('PRESCRIPTION', 'Prescription'),
        ('LAB_RESULT', 'Lab Result'),
        ('EMERGENCY', 'Emergency Visit'),
    ]
    
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='health_records')
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    visit_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_date']
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.title}"

class DoctorComment(models.Model):
    health_record = models.ForeignKey(HealthRecord, on_delete=models.CASCADE, related_name='doctor_comments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    comment = models.TextField()
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by Dr. {self.doctor.user.get_full_name()}"
