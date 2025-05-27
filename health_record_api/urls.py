from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/health-records/', include('health_records.urls')),
    path('api/notifications/', include('notifications.urls')),
]
