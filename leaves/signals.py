from django.db.models.signals import post_save, pre_save
import os
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)
from django.contrib.auth import get_user_model

from .models import LeaveRequest

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

# Email sending is now handled inline in views to ensure visible failures and avoid
# duplicate sends from signals. This module remains imported by the app package
# to keep signal import semantics stable; no handlers are active here.
def notify_on_leave_request(sender, instance, created, **kwargs):
    pass