"""
CKEditor image upload handler with Supabase Storage
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from core.storage import supabase_storage
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    """
    Upload image to Supabase Storage for CKEditor
    
    Returns:
        JSON with uploaded image URL
    """
    if 'upload' not in request.FILES:
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['upload']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return Response(
            {'error': 'Invalid file type. Only images allowed.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file size (max 5MB)
    if file.size > 5 * 1024 * 1024:
        return Response(
            {'error': 'File too large. Maximum size is 5MB.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Upload to Supabase
        url = supabase_storage.upload_file(file, folder='blog/images/')
        
        logger.info(f"Image uploaded successfully: {url}")
        
        # CKEditor expects this format
        return Response({
            'url': url,
            'uploaded': 1,
            'fileName': file.name,
        })
    
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        return Response(
            {'error': str(e), 'uploaded': 0},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
