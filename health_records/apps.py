from django.apps import AppConfig

class HealthRecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'health_records'
    
    def ready(self):
        import health_records.signals
