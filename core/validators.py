"""Security validators for passwords and file uploads"""
import re
import magic
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.conf import settings


class PasswordComplexityValidator:
    """Enforce strong password requirements"""
    
    def validate(self, password, user=None):
        min_length = getattr(settings, 'PASSWORD_MIN_LENGTH', 12)
        
        if len(password) < min_length:
            raise ValidationError(
                _(f"Password must be at least {min_length} characters long."),
                code='password_too_short',
            )
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
        
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter."),
                code='password_no_lower',
            )
        
        if not re.search(r'\d', password):
            raise ValidationError(
                _("Password must contain at least one digit."),
                code='password_no_digit',
            )
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("Password must contain at least one special character."),
                code='password_no_special',
            )
    
    def get_help_text(self):
        min_length = getattr(settings, 'PASSWORD_MIN_LENGTH', 12)
        return _(
            f"Password must be at least {min_length} characters and contain "
            "uppercase, lowercase, digit, and special character."
        )


class PasswordStrengthValidator:
    """Validate password strength - no common patterns"""
    
    def validate(self, password, user=None):
        # Check for sequential numbers
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            raise ValidationError(
                _("Password cannot contain sequential numbers."),
                code='password_sequential_numbers',
            )
        
        # Check for sequential letters
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            raise ValidationError(
                _("Password cannot contain sequential letters."),
                code='password_sequential_letters',
            )
        
        # Check for repeated characters
        if re.search(r'(.)\1{2,}', password):
            raise ValidationError(
                _("Password cannot contain more than 2 repeated characters."),
                code='password_repeated_chars',
            )
        
        # Check for common patterns
        common_patterns = ['password', 'admin', 'letmein', 'welcome', 'monkey', 'dragon', 'qwerty']
        if any(pattern in password.lower() for pattern in common_patterns):
            raise ValidationError(
                _("Password contains a common pattern."),
                code='password_common_pattern',
            )
    
    def get_help_text(self):
        return _("Password must not contain sequential characters, repeated characters, or common patterns.")


class FileValidator:
    """Validate uploaded files for security"""
    
    def __init__(self, allowed_extensions=None, max_size=None):
        self.allowed_extensions = allowed_extensions or ['jpg', 'jpeg', 'png', 'webp', 'gif']
        self.max_size = max_size or getattr(settings, 'MAX_UPLOAD_SIZE', 5242880)  # 5MB
    
    def __call__(self, file):
        # Check file size
        if file.size > self.max_size:
            raise ValidationError(
                f"File size exceeds maximum allowed size of {self.max_size / 1048576}MB."
            )
        
        # Check file extension
        ext = file.name.split('.')[-1].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(
                f"File extension '{ext}' not allowed. Allowed: {', '.join(self.allowed_extensions)}"
            )
        
        # Check MIME type using python-magic
        try:
            mime = magic.from_buffer(file.read(2048), mime=True)
            file.seek(0)  # Reset file pointer
            
            allowed_mimes = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'webp': 'image/webp',
                'gif': 'image/gif',
            }
            
            expected_mime = allowed_mimes.get(ext)
            if expected_mime and mime != expected_mime:
                raise ValidationError(
                    f"File content does not match extension. Expected {expected_mime}, got {mime}."
                )
        except Exception as e:
            raise ValidationError(f"Unable to validate file: {str(e)}")
        
        # Check for malicious content patterns
        file.seek(0)
        content = file.read(1024)
        file.seek(0)
        
        malicious_patterns = [
            b'<?php',
            b'<script',
            b'javascript:',
            b'eval(',
        ]
        
        for pattern in malicious_patterns:
            if pattern in content.lower():
                raise ValidationError("File contains potentially malicious content.")


def sanitize_filename(filename):
    """Sanitize filename to prevent directory traversal"""
    import os
    from django.utils.text import slugify
    
    # Remove path components
    filename = os.path.basename(filename)
    
    # Split name and extension
    name, ext = os.path.splitext(filename)
    
    # Slugify name and preserve extension
    safe_name = slugify(name)
    
    if not safe_name:
        safe_name = 'file'
    
    return f"{safe_name}{ext.lower()}"


def validate_ip_address(ip):
    """Validate IP address format"""
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
