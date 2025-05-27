from django.urls import path
from . import views

urlpatterns = [
    path('', views.HealthRecordListCreateView.as_view(), name='health-record-list'),
    path('<int:pk>/', views.HealthRecordDetailView.as_view(), name='health-record-detail'),
    path('<int:record_id>/comments/', views.add_doctor_comment, name='add-doctor-comment'),
    path('my-patients/', views.my_patients, name='my-patients'),
]
