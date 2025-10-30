"""
Image upload API endpoint - Upload images to Supabase Storage
"""
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from core.storage import supabase_storage
from .models import ImageAsset
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request):
    """
    Upload image to Supabase Storage
    
    POST /api/v1/images/upload/
    
    Request (multipart/form-data):
        - image: Image file (required)
        - alt_text: Alt text for SEO (optional)
        - folder: Custom folder path (optional, default: blog-images/)
    
    Response:
        {
            "id": "uuid",
            "url": "https://supabase.co/storage/...",
            "alt_text": "Image description",
            "width": 1920,
            "height": 1080,
            "format": "webp"
        }
    """
    if 'image' not in request.FILES:
        return Response(
            {'error': 'No image file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['image']
    alt_text = request.data.get('alt_text', file.name)
    folder = request.data.get('folder', 'blog-images/')
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return Response(
            {'error': 'Invalid file type. Only JPEG, PNG, GIF, and WebP allowed.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file size (max 10MB)
    if file.size > 10 * 1024 * 1024:
        return Response(
            {'error': 'File too large. Maximum size is 10MB.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get image dimensions
        image = Image.open(file)
        width, height = image.size
        format_type = image.format.lower() if image.format else 'unknown'
        
        # Reset file pointer
        file.seek(0)
        
        # Upload to Supabase with SEO-friendly filename
        url = supabase_storage.upload_file(
            file, 
            folder=folder,
            filename=alt_text
        )
        
        # Create ImageAsset record
        image_asset = ImageAsset.objects.create(
            file=url,
            alt_text=alt_text,
            width=width,
            height=height,
            format=format_type
        )
        
        logger.info(f"Image uploaded: {url} (ID: {image_asset.id})")
        
        return Response({
            'id': str(image_asset.id),
            'url': url,
            'alt_text': alt_text,
            'width': width,
            'height': height,
            'format': format_type
        }, status=status.HTTP_201_CREATED)
    
    except (IOError, OSError) as e:
        logger.error(f"File I/O error: {str(e)}")
        return Response(
            {'error': 'Failed to process image file'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error in image upload: {str(e)}")
        return Response(
            {'error': 'Upload failed. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
