from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import JsonResponse 


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
        'documentation': '/api-docs/',
        'admin': '/admin/',
        'health': '/health/',
        'api': {
            'auth': '/api/auth/',
            'health_records': '/api/health-records/',
            'notifications': '/api/notifications/'
        }
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

def api_docs(request):
    return JsonResponse({
        'title': 'Health Record API - Complete Documentation',
        'version': '1.0.0',
        'description': 'A secure REST API for managing personal health records with patient-doctor relationships',
        'base_url': 'https://health-record-api-assessment-production.up.railway.app',
        'authentication': {
            'type': 'JWT Bearer Token',
            'header': 'Authorization: Bearer <access_token>',
            'token_lifetime': '5 minutes',
            'refresh_token_lifetime': '1 day'
        },
        'endpoints': {
            'Authentication': {
                'POST /api/auth/register/': {
                    'description': 'Register new user (Patient or Doctor)',
                    'body': {
                        'username': 'string (required)',
                        'email': 'string (required)', 
                        'password': 'string (required, min 8 chars)',
                        'password_confirm': 'string (required)',
                        'first_name': 'string (required)',
                        'last_name': 'string (required)',
                        'user_type': 'PATIENT or DOCTOR (required)',
                        'phone_number': 'string (optional)',
                        'date_of_birth': 'YYYY-MM-DD (optional)'
                    },
                    'response': 'User object + JWT tokens',
                    'auth_required': False
                },
                'POST /api/auth/login/': {
                    'description': 'Login and get JWT tokens',
                    'body': {
                        'username': 'string (required)',
                        'password': 'string (required)'
                    },
                    'response': 'User object + JWT tokens',
                    'auth_required': False
                },
                'POST /api/auth/token/refresh/': {
                    'description': 'Refresh access token',
                    'body': {
                        'refresh': 'string (required)'
                    },
                    'response': 'New access token',
                    'auth_required': False
                },
                'GET /api/auth/profile/': {
                    'description': 'Get current user profile',
                    'response': 'User profile (Patient/Doctor specific)',
                    'auth_required': True
                },
                'PUT /api/auth/profile/': {
                    'description': 'Update user profile', 
                    'body': 'Profile fields to update',
                    'auth_required': True
                },
                'GET /api/auth/doctors/': {
                    'description': 'List all available doctors',
                    'response': 'Array of doctor profiles',
                    'auth_required': True
                },
                'POST /api/auth/assign-doctor/': {
                    'description': 'Assign doctor to patient (doctors/admin only)',
                    'body': {
                        'patient_id': 'integer (required)',
                        'doctor_id': 'integer (optional, defaults to current user)'
                    },
                    'auth_required': True,
                    'permissions': 'Doctor or Admin'
                }
            },
            'Health Records': {
                'GET /api/health-records/': {
                    'description': 'List health records (patients: own records, doctors: assigned patients)',
                    'response': 'Paginated list of health records',
                    'auth_required': True
                },
                'POST /api/health-records/': {
                    'description': 'Create new health record (patients only)',
                    'body': {
                        'record_type': 'CHECKUP, DIAGNOSIS, PRESCRIPTION, LAB_RESULT, or EMERGENCY (required)',
                        'title': 'string (required)',
                        'description': 'string (optional)',
                        'symptoms': 'string (optional)',
                        'diagnosis': 'string (optional)',
                        'treatment': 'string (optional)',
                        'medications': 'string (optional)',
                        'visit_date': 'ISO datetime (required)'
                    },
                    'response': 'Created health record',
                    'auth_required': True,
                    'permissions': 'Patients only'
                },
                'GET /api/health-records/{id}/': {
                    'description': 'Get specific health record',
                    'response': 'Health record with doctor comments',
                    'auth_required': True,
                    'permissions': 'Record owner or assigned doctor'
                },
                'PUT /api/health-records/{id}/': {
                    'description': 'Update health record (patients only)',
                    'body': 'Health record fields to update',
                    'auth_required': True,
                    'permissions': 'Record owner only'
                },
                'DELETE /api/health-records/{id}/': {
                    'description': 'Delete health record (patients only)',
                    'auth_required': True,
                    'permissions': 'Record owner only'
                },
                'POST /api/health-records/{id}/comments/': {
                    'description': 'Add doctor comment to health record',
                    'body': {
                        'comment': 'string (required)',
                        'is_private': 'boolean (optional, default: false)'
                    },
                    'response': 'Created comment',
                    'auth_required': True,
                    'permissions': 'Assigned doctor only'
                },
                'GET /api/health-records/my-patients/': {
                    'description': 'List patients assigned to current doctor',
                    'response': 'Array of patient summaries with record counts',
                    'auth_required': True,
                    'permissions': 'Doctors only'
                }
            },
            'Notifications': {
                'GET /api/notifications/': {
                    'description': 'List user notifications',
                    'response': 'Paginated list of notifications',
                    'auth_required': True
                },
                'POST /api/notifications/{id}/read/': {
                    'description': 'Mark specific notification as read',
                    'response': 'Success message',
                    'auth_required': True
                },
                'POST /api/notifications/mark-all-read/': {
                    'description': 'Mark all notifications as read',
                    'response': 'Count of notifications marked as read',
                    'auth_required': True
                }
            }
        },
        'example_requests': {
            'register_patient': {
                'url': '/api/auth/register/',
                'method': 'POST',
                'body': {
                    'username': 'patient1',
                    'email': 'patient@example.com',
                    'password': 'securepass123',
                    'password_confirm': 'securepass123',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'user_type': 'PATIENT'
                }
            },
            'login': {
                'url': '/api/auth/login/',
                'method': 'POST', 
                'body': {
                    'username': 'patient1',
                    'password': 'securepass123'
                }
            },
            'create_health_record': {
                'url': '/api/health-records/',
                'method': 'POST',
                'headers': {
                    'Authorization': 'Bearer <access_token>',
                    'Content-Type': 'application/json'
                },
                'body': {
                    'record_type': 'CHECKUP',
                    'title': 'Annual Physical',
                    'description': 'Routine annual health checkup',
                    'visit_date': '2025-05-28T10:00:00Z'
                }
            }
        },
        'response_codes': {
            '200': 'Success',
            '201': 'Created',
            '400': 'Bad Request - Validation errors',
            '401': 'Unauthorized - Authentication required',
            '403': 'Forbidden - Insufficient permissions',
            '404': 'Not Found',
            '500': 'Internal Server Error'
        },
        'security_features': [
            'JWT token-based authentication',
            'Role-based access control (Patient/Doctor)',
            'Data isolation (patients see own records only)',
            'Doctor assignment verification',
            'Short-lived tokens (5 minutes)',
            'Automatic token refresh'
        ]
    })


urlpatterns = [
    path('', root_view, name='root'),  
    path('health/', health_check, name='health-check'),  
    path('admin/', admin.site.urls),
    path('api-docs/', api_docs, name='api-docs'),
    path('api/auth/', include('accounts.urls')),
    path('api/health-records/', include('health_records.urls')),
    path('api/notifications/', include('notifications.urls')),


    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Default to swagger
]
