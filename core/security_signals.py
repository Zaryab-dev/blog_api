"""Security event signals and handlers"""
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from axes.signals import user_locked_out
from django.contrib.auth.signals import user_login_failed, user_logged_in
import logging

logger = logging.getLogger('security')


@receiver(user_locked_out)
def handle_user_locked_out(sender, request, username, **kwargs):
    """Handle account lockout event"""
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    
    logger.warning(
        f"Account locked out - Username: {username}, IP: {ip_address}, "
        f"User-Agent: {user_agent}"
    )
    
    # Send email alert
    if getattr(settings, 'SECURITY_EMAIL_ALERTS', False):
        send_security_alert(
            subject='🔒 Account Lockout Alert',
            message=f"""
            An account has been locked due to multiple failed login attempts.
            
            Details:
            - Username: {username}
            - IP Address: {ip_address}
            - User Agent: {user_agent}
            - Time: {request.META.get('HTTP_DATE', 'Unknown')}
            
            The account will be automatically unlocked after 1 hour.
            """,
            recipient=getattr(settings, 'SECURITY_ALERT_EMAIL', settings.ADMIN_EMAIL)
        )


@receiver(user_login_failed)
def handle_login_failed(sender, credentials, request, **kwargs):
    """Handle failed login attempt"""
    username = credentials.get('username', 'Unknown')
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
    
    logger.warning(
        f"Failed login attempt - Username: {username}, IP: {ip_address}"
    )


@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    """Handle successful login"""
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
    
    # Only log admin logins
    if request.path.startswith('/admin'):
        logger.info(
            f"Admin login successful - User: {user.username}, IP: {ip_address}"
        )
        
        # Send email for admin logins if enabled
        if getattr(settings, 'SECURITY_EMAIL_ALERTS', False) and user.is_superuser:
            send_security_alert(
                subject='✅ Admin Login Notification',
                message=f"""
                An admin user has logged in.
                
                Details:
                - Username: {user.username}
                - IP Address: {ip_address}
                - Time: {request.META.get('HTTP_DATE', 'Unknown')}
                
                If this wasn't you, please secure your account immediately.
                """,
                recipient=user.email or getattr(settings, 'SECURITY_ALERT_EMAIL', settings.ADMIN_EMAIL)
            )


def send_security_alert(subject, message, recipient):
    """Send security alert email"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send security alert email: {e}")
