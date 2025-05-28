from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer, MessageResponseSerializer

class NotificationListView(generics.ListAPIView):
    """
    User Notifications
    
    GET: List all notifications for the current user
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="List Notifications",
        operation_description="Get all notifications for the current authenticated user",
        tags=['Notifications'],
        responses={
            200: NotificationSerializer(many=True),
            401: openapi.Response(description="Authentication required")
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

@swagger_auto_schema(
    method='post',
    operation_summary="Mark Notification as Read",
    operation_description="Mark a specific notification as read",
    tags=['Notifications'],
    manual_parameters=[
        openapi.Parameter('notification_id', openapi.IN_PATH, description="Notification ID", type=openapi.TYPE_INTEGER, required=True)
    ],
    responses={
        200: MessageResponseSerializer,
        404: openapi.Response(description="Notification not found"),
        401: openapi.Response(description="Authentication required")
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@swagger_auto_schema(
    method='post',
    operation_summary="Mark All Notifications as Read",
    operation_description="Mark all unread notifications as read for the current user",
    tags=['Notifications'],
    responses={
        200: MessageResponseSerializer,
        401: openapi.Response(description="Authentication required")
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all unread notifications as read"""
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    count = notifications.update(is_read=True)
    return Response({'message': f'{count} notifications marked as read'})