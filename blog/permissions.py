"""Enhanced DRF permissions with security logging"""
import logging
from rest_framework import permissions
from core.security_utils import log_security_event

logger = logging.getLogger('security')


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to everyone
    Allow write access only to admin users
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        is_allowed = request.user and request.user.is_staff
        
        if not is_allowed:
            log_security_event(
                'unauthorized_write_attempt',
                f'Non-admin user attempted {request.method} on {view.__class__.__name__}',
                request,
                severity='WARNING'
            )
        
        return is_allowed


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners to edit
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if object has owner/author field
        owner = getattr(obj, 'author', None) or getattr(obj, 'user', None) or getattr(obj, 'owner', None)
        
        is_owner = owner == request.user
        
        if not is_owner:
            log_security_event(
                'unauthorized_object_access',
                f'User {request.user} attempted to modify object owned by {owner}',
                request,
                severity='WARNING'
            )
        
        return is_owner


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to everyone
    Require authentication for write operations
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated
