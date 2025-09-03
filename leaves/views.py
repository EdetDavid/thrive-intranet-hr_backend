from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import LeaveRequest
from .serializers import LeaveRequestSerializer
import logging
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
import os

logger = logging.getLogger(__name__)
User = get_user_model()


class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Log incoming create attempts: who and what payload
        try:
            logger.info('LeaveRequest create called by user=%s payload=%s', getattr(request.user, 'id', None), request.data)
        except Exception:
            logger.exception('Failed to log incoming leave create request for user=%s', getattr(request.user, 'id', None))

        # Proceed with normal creation flow
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Attempt to send notification inline (for debugging) using same templates as signals
        try:
            # Refresh instance to have all fields
            lr = LeaveRequest.objects.select_related('user').filter(pk=serializer.instance.id).first()
            if lr:
                recipients = []
                manager = getattr(lr.user, 'manager', None)
                if manager and getattr(manager, 'email', None):
                    recipients.append(manager.email)
                hr_emails = list(User.objects.filter(is_hr=True).exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True))
                recipients.extend(hr_emails)
                recipients = [e for e in dict.fromkeys(recipients) if e]

                context = {
                    'user': lr.user,
                    'leave': lr,
                    'app_url': getattr(settings, 'APP_BASE_URL', 'http://localhost:3000'),
                }
                html_content = render_to_string('leaves/leave_notification.html', context)
                text_content = render_to_string('leaves/leave_notification.txt', context)
                subject = f"Leave request: {lr.user.get_full_name() or lr.user.username} ({lr.leave_type})"
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or None

                # Make sure we log what we will send
                logger.info('Inline send: backend=%s from=%s to=%s', getattr(settings, 'EMAIL_BACKEND', 'unknown'), from_email, recipients)
                try:
                    # In debug, force fail_silently False to see exceptions
                    force_fail_silently = not getattr(settings, 'DEBUG', False)
                    msg = EmailMultiAlternatives(subject, strip_tags(text_content), from_email, recipients)
                    msg.attach_alternative(html_content, 'text/html')
                    msg.send(fail_silently=force_fail_silently)
                    logger.info('Inline email send succeeded for leave %s', lr.id)
                except Exception:
                    logger.exception('Inline email send failed for leave %s', lr.id)
        except Exception:
            logger.exception('Unexpected error during inline email send after create')

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        user = self.request.user
        # optional filter param to see leaves for a specific user
        user_param = self.request.query_params.get('user', None)
        if user_param is not None:
            try:
                user_id = int(user_param)
            except (ValueError, TypeError):
                return LeaveRequest.objects.none()

            # HR can view any user's leaves
            if getattr(user, 'is_hr', False):
                return LeaveRequest.objects.filter(user_id=user_id).select_related('user', 'approver')

            # Line managers can view leaves only for their subordinates
            if getattr(user, 'is_line_manager', False):
                # ensure the target user's manager is the current user
                return LeaveRequest.objects.filter(user__manager_id=user.id, user_id=user_id).select_related('user', 'approver')

            # Regular users can view only their own
            if user.id == user_id:
                return LeaveRequest.objects.filter(user=user).select_related('user', 'approver')

            return LeaveRequest.objects.none()
        # HR and line managers can see all requests
        if getattr(user, 'is_hr', False):
            return LeaveRequest.objects.all().select_related('user', 'approver')

        # Line managers see only requests from users who report to them (their subordinates)
        if getattr(user, 'is_line_manager', False):
            return LeaveRequest.objects.filter(user__manager=user).select_related('user', 'approver')

        # Regular users see only their requests
        return LeaveRequest.objects.filter(user=user).select_related('user', 'approver')

    def perform_create(self, serializer):
        lr = serializer.save(user=self.request.user)
        # Log creation and resolved recipients for debugging
        try:
            recipients = []
            manager = getattr(lr.user, 'manager', None)
            if manager and getattr(manager, 'email', None):
                recipients.append(manager.email)
            hr_emails = list(User.objects.filter(is_hr=True).exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True))
            recipients.extend(hr_emails)
            recipients = [e for e in dict.fromkeys(recipients) if e]
            logger.info('LeaveRequest created id=%s user=%s recipients=%s', lr.id, lr.user_id, recipients)
        except Exception:
            logger.exception('Error logging recipients for leave %s', getattr(lr, 'id', None))

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user = request.user
        if not (getattr(user, 'is_hr', False) or getattr(user, 'is_line_manager', False)):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        lr = get_object_or_404(LeaveRequest, pk=pk)
        # If caller is a line manager, ensure they manage the request user
        if getattr(user, 'is_line_manager', False) and lr.user.manager_id != user.id:
            return Response({'detail': 'Not authorized to approve this user\'s request'}, status=status.HTTP_403_FORBIDDEN)
        lr.status = 'approved'
        lr.approver = user
        lr.save()

        # Build admin recipients: manager + HR (informational)
        try:
            admin_recipients = []
            manager = getattr(lr.user, 'manager', None)
            if manager and getattr(manager, 'email', None):
                admin_recipients.append(manager.email)
            hr_emails = list(User.objects.filter(is_hr=True).exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True))
            admin_recipients.extend(hr_emails)
            admin_recipients = [e for e in dict.fromkeys(admin_recipients) if e]

            # Send informational email to manager + HR
            if admin_recipients:
                subject_admin = f"Leave request of {lr.user.get_full_name() or lr.user.username} has been approved by {user.get_full_name() or user.username}"
                ctx_admin = {
                    'user': lr.user,
                    'leave': lr,
                    'approver': user,
                    'recipient_name': ', '.join(admin_recipients),
                    'for_requester': False,
                }
                html_admin = render_to_string('leaves/leave_approved.html', ctx_admin)
                text_admin = render_to_string('leaves/leave_approved.txt', ctx_admin)
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or None
                try:
                    msg_admin = EmailMultiAlternatives(subject_admin, strip_tags(text_admin), from_email, admin_recipients)
                    msg_admin.attach_alternative(html_admin, 'text/html')
                    msg_admin.send(fail_silently=not getattr(settings, 'DEBUG', False))
                    logger.info('Sent admin approval email for leave %s to %s', lr.id, admin_recipients)
                except Exception:
                    logger.exception('Failed to send admin approval email for leave %s', lr.id)

            # Send user-facing email to requester
            if getattr(lr.user, 'email', None):
                subject_user = 'Your Leave Request Has Been Accepted'
                ctx_user = {
                    'user': lr.user,
                    'leave': lr,
                    'approver': user,
                    'recipient_name': lr.user.get_full_name() or lr.user.username,
                    'for_requester': True,
                }
                html_user = render_to_string('leaves/leave_approved.html', ctx_user)
                text_user = render_to_string('leaves/leave_approved.txt', ctx_user)
                try:
                    msg_user = EmailMultiAlternatives(subject_user, strip_tags(text_user), from_email, [lr.user.email])
                    msg_user.attach_alternative(html_user, 'text/html')
                    msg_user.send(fail_silently=not getattr(settings, 'DEBUG', False))
                    logger.info('Sent requester approval email for leave %s to %s', lr.id, lr.user.email)
                except Exception:
                    logger.exception('Failed to send requester approval email for leave %s', lr.id)
        except Exception:
            logger.exception('Unexpected error sending approval notifications for leave %s', lr.id)

        return Response(LeaveRequestSerializer(lr).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        user = request.user
        if not (getattr(user, 'is_hr', False) or getattr(user, 'is_line_manager', False)):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        lr = get_object_or_404(LeaveRequest, pk=pk)
        # If caller is a line manager, ensure they manage the request user
        if getattr(user, 'is_line_manager', False) and lr.user.manager_id != user.id:
            return Response({'detail': 'Not authorized to reject this user\'s request'}, status=status.HTTP_403_FORBIDDEN)
        lr.status = 'rejected'
        lr.approver = user
        lr.save()

        # Build admin recipients: manager + HR (informational)
        try:
            admin_recipients = []
            manager = getattr(lr.user, 'manager', None)
            if manager and getattr(manager, 'email', None):
                admin_recipients.append(manager.email)
            hr_emails = list(User.objects.filter(is_hr=True).exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True))
            admin_recipients.extend(hr_emails)
            admin_recipients = [e for e in dict.fromkeys(admin_recipients) if e]

            # Send informational email to manager + HR
            if admin_recipients:
                subject_admin = f"Leave request of {lr.user.get_full_name() or lr.user.username} has been rejected by {user.get_full_name() or user.username}"
                ctx_admin = {
                    'user': lr.user,
                    'leave': lr,
                    'approver': user,
                    'recipient_name': ', '.join(admin_recipients),
                    'for_requester': False,
                }
                html_admin = render_to_string('leaves/leave_rejected.html', ctx_admin)
                text_admin = render_to_string('leaves/leave_rejected.txt', ctx_admin)
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or None
                try:
                    msg_admin = EmailMultiAlternatives(subject_admin, strip_tags(text_admin), from_email, admin_recipients)
                    msg_admin.attach_alternative(html_admin, 'text/html')
                    msg_admin.send(fail_silently=not getattr(settings, 'DEBUG', False))
                    logger.info('Sent admin rejection email for leave %s to %s', lr.id, admin_recipients)
                except Exception:
                    logger.exception('Failed to send admin rejection email for leave %s', lr.id)

            # Send user-facing email to requester
            if getattr(lr.user, 'email', None):
                subject_user = 'Your Leave Request Has Been Rejected'
                ctx_user = {
                    'user': lr.user,
                    'leave': lr,
                    'approver': user,
                    'recipient_name': lr.user.get_full_name() or lr.user.username,
                    'for_requester': True,
                }
                html_user = render_to_string('leaves/leave_rejected.html', ctx_user)
                text_user = render_to_string('leaves/leave_rejected.txt', ctx_user)
                try:
                    msg_user = EmailMultiAlternatives(subject_user, strip_tags(text_user), from_email, [lr.user.email])
                    msg_user.attach_alternative(html_user, 'text/html')
                    msg_user.send(fail_silently=not getattr(settings, 'DEBUG', False))
                    logger.info('Sent requester rejection email for leave %s to %s', lr.id, lr.user.email)
                except Exception:
                    logger.exception('Failed to send requester rejection email for leave %s', lr.id)
        except Exception:
            logger.exception('Unexpected error sending rejection notifications for leave %s', lr.id)

        return Response(LeaveRequestSerializer(lr).data)
