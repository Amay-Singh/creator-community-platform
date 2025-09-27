"""
Two-Factor Authentication implementation
"""
import pyotp
import qrcode
import io
import base64
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class TwoFactorManager:
    """
    Manage two-factor authentication for users
    """
    
    @staticmethod
    def generate_secret_key(user):
        """Generate a new secret key for user"""
        secret = pyotp.random_base32()
        
        # Store secret in user profile or separate model
        # For now, we'll use cache (in production, use encrypted database field)
        cache_key = f"2fa_secret:{user.id}"
        cache.set(cache_key, secret, 60 * 60 * 24)  # 24 hours
        
        return secret
    
    @staticmethod
    def get_secret_key(user):
        """Get user's secret key"""
        cache_key = f"2fa_secret:{user.id}"
        return cache.get(cache_key)
    
    @staticmethod
    def generate_qr_code(user, secret):
        """Generate QR code for authenticator app setup"""
        # Create provisioning URI
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name="Creator Community Platform"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 string
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_token(user, token):
        """Verify TOTP token"""
        secret = TwoFactorManager.get_secret_key(user)
        if not secret:
            return False
        
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # Allow 30 second window
    
    @staticmethod
    def enable_2fa(user, secret):
        """Enable 2FA for user"""
        # In production, store in encrypted database field
        cache_key = f"2fa_enabled:{user.id}"
        cache.set(cache_key, secret, None)  # No expiration
        
        logger.info(f"2FA enabled for user {user.id}")
    
    @staticmethod
    def disable_2fa(user):
        """Disable 2FA for user"""
        cache_key = f"2fa_enabled:{user.id}"
        cache.delete(cache_key)
        
        # Also remove setup secret
        setup_key = f"2fa_secret:{user.id}"
        cache.delete(setup_key)
        
        logger.info(f"2FA disabled for user {user.id}")
    
    @staticmethod
    def is_2fa_enabled(user):
        """Check if 2FA is enabled for user"""
        cache_key = f"2fa_enabled:{user.id}"
        return cache.get(cache_key) is not None
    
    @staticmethod
    def generate_backup_codes(user):
        """Generate backup codes for 2FA recovery"""
        import secrets
        import string
        
        codes = []
        for _ in range(10):
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            codes.append(f"{code[:4]}-{code[4:]}")
        
        # Store backup codes (in production, hash and store in database)
        cache_key = f"2fa_backup_codes:{user.id}"
        cache.set(cache_key, codes, None)
        
        return codes
    
    @staticmethod
    def verify_backup_code(user, code):
        """Verify and consume backup code"""
        cache_key = f"2fa_backup_codes:{user.id}"
        codes = cache.get(cache_key, [])
        
        if code in codes:
            # Remove used code
            codes.remove(code)
            cache.set(cache_key, codes, None)
            logger.info(f"Backup code used for user {user.id}")
            return True
        
        return False


# Serializers
class Setup2FASerializer(serializers.Serializer):
    """Serializer for 2FA setup"""
    pass


class Verify2FASerializer(serializers.Serializer):
    """Serializer for 2FA verification"""
    token = serializers.CharField(max_length=6, min_length=6)


class Enable2FASerializer(serializers.Serializer):
    """Serializer for enabling 2FA"""
    token = serializers.CharField(max_length=6, min_length=6)


class Disable2FASerializer(serializers.Serializer):
    """Serializer for disabling 2FA"""
    token = serializers.CharField(max_length=6, min_length=6, required=False)
    backup_code = serializers.CharField(max_length=9, required=False)
    
    def validate(self, data):
        if not data.get('token') and not data.get('backup_code'):
            raise serializers.ValidationError("Either token or backup_code is required")
        return data


# API Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_2fa(request):
    """
    POST /api/auth/2fa/setup/
    Generate QR code for 2FA setup
    """
    try:
        user = request.user
        
        # Check if 2FA is already enabled
        if TwoFactorManager.is_2fa_enabled(user):
            return Response({
                'error': '2FA is already enabled for this account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate secret key
        secret = TwoFactorManager.generate_secret_key(user)
        
        # Generate QR code
        qr_code = TwoFactorManager.generate_qr_code(user, secret)
        
        return Response({
            'qr_code': qr_code,
            'secret': secret,
            'message': 'Scan the QR code with your authenticator app, then verify with a token to enable 2FA'
        })
        
    except Exception as e:
        logger.error(f"2FA setup error for user {request.user.id}: {e}")
        return Response({
            'error': 'Failed to setup 2FA'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """
    POST /api/auth/2fa/enable/
    Enable 2FA after token verification
    """
    try:
        serializer = Enable2FASerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        token = serializer.validated_data['token']
        
        # Verify token
        if not TwoFactorManager.verify_token(user, token):
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Enable 2FA
        secret = TwoFactorManager.get_secret_key(user)
        TwoFactorManager.enable_2fa(user, secret)
        
        # Generate backup codes
        backup_codes = TwoFactorManager.generate_backup_codes(user)
        
        return Response({
            'message': '2FA enabled successfully',
            'backup_codes': backup_codes,
            'warning': 'Save these backup codes in a secure location. They can be used to access your account if you lose your authenticator device.'
        })
        
    except Exception as e:
        logger.error(f"2FA enable error for user {request.user.id}: {e}")
        return Response({
            'error': 'Failed to enable 2FA'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """
    POST /api/auth/2fa/disable/
    Disable 2FA after verification
    """
    try:
        serializer = Disable2FASerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        # Check if 2FA is enabled
        if not TwoFactorManager.is_2fa_enabled(user):
            return Response({
                'error': '2FA is not enabled for this account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify token or backup code
        token = serializer.validated_data.get('token')
        backup_code = serializer.validated_data.get('backup_code')
        
        verified = False
        if token:
            verified = TwoFactorManager.verify_token(user, token)
        elif backup_code:
            verified = TwoFactorManager.verify_backup_code(user, backup_code)
        
        if not verified:
            return Response({
                'error': 'Invalid token or backup code'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Disable 2FA
        TwoFactorManager.disable_2fa(user)
        
        return Response({
            'message': '2FA disabled successfully'
        })
        
    except Exception as e:
        logger.error(f"2FA disable error for user {request.user.id}: {e}")
        return Response({
            'error': 'Failed to disable 2FA'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa(request):
    """
    POST /api/auth/2fa/verify/
    Verify 2FA token
    """
    try:
        serializer = Verify2FASerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        token = serializer.validated_data['token']
        
        # Verify token
        if TwoFactorManager.verify_token(user, token):
            return Response({
                'message': 'Token verified successfully',
                'verified': True
            })
        else:
            return Response({
                'error': 'Invalid token',
                'verified': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"2FA verify error for user {request.user.id}: {e}")
        return Response({
            'error': 'Failed to verify token'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_2fa_status(request):
    """
    GET /api/auth/2fa/status/
    Get 2FA status for user
    """
    try:
        user = request.user
        is_enabled = TwoFactorManager.is_2fa_enabled(user)
        
        return Response({
            'enabled': is_enabled,
            'user_id': user.id
        })
        
    except Exception as e:
        logger.error(f"2FA status error for user {request.user.id}: {e}")
        return Response({
            'error': 'Failed to get 2FA status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
