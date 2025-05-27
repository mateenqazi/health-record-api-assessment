from celery import shared_task
from .models import Notification

@shared_task
def send_patient_assignment_notification(doctor_id, patient_name):
    """Send notification when a patient is assigned to a doctor"""
    from accounts.models import User
    
    try:
        doctor = User.objects.get(id=doctor_id)
        Notification.objects.create(
            recipient=doctor,
            notification_type='PATIENT_ASSIGNED',
            title='New Patient Assigned',
            message=f'You have been assigned a new patient: {patient_name}'
        )
    except User.DoesNotExist:
        pass

@shared_task
def send_new_record_notification(doctor_id, patient_name, record_title):
    """Send notification when a patient creates a new health record"""
    from accounts.models import User
    
    try:
        doctor = User.objects.get(id=doctor_id)
        Notification.objects.create(
            recipient=doctor,
            notification_type='NEW_RECORD',
            title='New Health Record',
            message=f'{patient_name} has created a new health record: {record_title}'
        )
    except User.DoesNotExist:
        pass
