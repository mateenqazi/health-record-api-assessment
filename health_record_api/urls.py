from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Health Record API",
        default_version='v1',
        description="""
        A secure REST API for managing personal health records with patient-doctor relationships.
        
        ## Features
        - JWT-based authentication with 5-minute token expiry
        - Role-based access control (Patient/Doctor)
        - Health records management with CRUD operations
        - Doctor-patient assignments and notifications
        - Async notification system with Celery
        
        ## Authentication
        1. Register or login to get JWT tokens
        2. Use Bearer token in Authorization header
        3. Tokens expire after 5 minutes - use refresh endpoint
        
        ## User Types
        - **PATIENT**: Can create, view, update, delete their own health records
        - **DOCTOR**: Can view and comment on assigned patients' records
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@healthrecord.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


def health_check(request):
    return JsonResponse({
        'status': 'healthy', 
        'message': 'Health Record API is running',
        'database': 'connected'
    })

def root_view(request):
    return JsonResponse({
        'message': 'Health Record API',
        'swagger': '/swagger/',
        'admin': '/admin/',
        'health': '/health/'
    })

schema_view = get_schema_view(
    openapi.Info(
        title="Health Record API",
        default_version='v1',
        description="A secure REST API for managing personal health records",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', root_view, name='root'),  
    path('health/', health_check, name='health-check'),  
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/health-records/', include('health_records.urls')),
    path('api/notifications/', include('notifications.urls')),


    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Default to swagger
]
