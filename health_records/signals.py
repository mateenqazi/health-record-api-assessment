from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import HealthRecord
from notifications.tasks import send_new_record_notification

@receiver(post_save, sender=HealthRecord)
def notify_doctor_new_record(sender, instance, created, **kwargs):
    """Send notification to assigned doctor when patient creates new record"""
    if created and instance.patient.assigned_doctor:
        send_new_record_notification.delay(
            instance.patient.assigned_doctor.user.id,
            instance.patient.user.get_full_name(),
            instance.title
        )
