"""Secure JWT authentication with rate limiting and logging"""
import logging
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.conf import settings
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

logger = logging.getLogger('security')


class LoginAttemptTracker:
    """Track and limit login attempts"""
    
    @staticmethod
    def get_cache_key(identifier):
        return f"login_attempts:{identifier}"
    
    @staticmethod
    def get_lockout_key(identifier):
        return f"account_locked:{identifier}"
    
    @classmethod
    def is_locked(cls, identifier):
        """Check if account is locked"""
        return cache.get(cls.get_lockout_key(identifier), False)
    
    @classmethod
    def record_failed_attempt(cls, identifier):
        """Record failed login attempt"""
        max_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
        lockout_duration = getattr(settings, 'ACCOUNT_LOCKOUT_DURATION', 900)  # 15 min
        
        cache_key = cls.get_cache_key(identifier)
        attempts = cache.get(cache_key, 0) + 1
        cache.set(cache_key, attempts, 3600)  # Track for 1 hour
        
        if attempts >= max_attempts:
            cache.set(cls.get_lockout_key(identifier), True, lockout_duration)
            logger.warning(f"Account locked due to failed attempts: {identifier}")
            return True
        
        return False
    
    @classmethod
    def reset_attempts(cls, identifier):
        """Reset login attempts on successful login"""
        cache.delete(cls.get_cache_key(identifier))
        cache.delete(cls.get_lockout_key(identifier))


class SecureTokenObtainSerializer(serializers.Serializer):
    """Custom JWT serializer with security logging"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        # Check if account is locked
        if LoginAttemptTracker.is_locked(username):
            logger.warning(f"Login attempt on locked account: {username}")
            raise serializers.ValidationError(
                "Account temporarily locked. Try again later."
            )
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is None:
            # Record failed attempt
            is_locked = LoginAttemptTracker.record_failed_attempt(username)
            logger.warning(f"Failed login attempt for: {username}")
            
            if is_locked:
                raise serializers.ValidationError(
                    "Too many failed attempts. Account locked temporarily."
                )
            
            raise serializers.ValidationError("Invalid credentials.")
        
        if not user.is_active:
            logger.warning(f"Login attempt on inactive account: {username}")
            raise serializers.ValidationError("Account is disabled.")
        
        # Reset attempts on successful login
        LoginAttemptTracker.reset_attempts(username)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims
        refresh['username'] = user.username
        refresh['email'] = user.email
        
        # Log successful login
        logger.info(f"Successful login: {username}")
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }


class SecureTokenObtainView(TokenObtainPairView):
    """Secure JWT token endpoint with rate limiting"""
    permission_classes = [AllowAny]
    serializer_class = SecureTokenObtainSerializer
    throttle_scope = 'login'


class LogoutView(APIView):
    """Logout endpoint with token blacklisting"""
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logger.info(f"User logged out: {request.user.username if request.user.is_authenticated else 'anonymous'}")
            
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )
