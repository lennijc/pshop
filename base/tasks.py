from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import reservation
from datetime import timedelta

@shared_task
def send_email_task(subject, message, recipient_email):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # This will use the sender email set in your SMTP settings
        [recipient_email]
    )


@shared_task
def delete_expired_reservations():
    expired_time = timezone.now() - timedelta(minutes=2)
    reservation.objects.filter(status='pending', createdAt__lt=expired_time).delete()