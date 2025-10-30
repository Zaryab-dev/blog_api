"""
CKEditor 5 custom upload view for Supabase Storage
"""
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from core.storage import supabase_storage
from supabase.lib.client_options import ClientOptions
import logging

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/jpg']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@staff_member_required
@require_http_methods(["POST"])
def ckeditor5_upload(request):
    """
    Handle CKEditor 5 image uploads to Supabase Storage.
    Only accessible to admin/staff users.
    
    Expected request: POST with 'upload' file field
    Returns: JSON with 'url' or 'error' field
    """
    if request.method != 'POST':
        return JsonResponse({'error': {'message': 'Method not allowed'}}, status=405)
    
    file = request.FILES.get('upload')
    if not file:
        return JsonResponse({'error': {'message': 'No file provided'}}, status=400)
    
    logger.info(f"CKEditor upload: {file.name} ({file.size} bytes, {file.content_type})")
    
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        return JsonResponse({
            'error': {'message': f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"}
        }, status=400)
    
    # Validate file size
    if file.size > MAX_FILE_SIZE:
        return JsonResponse({
            'error': {'message': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'}
        }, status=400)
    
    try:
        # Upload to Supabase
        url = supabase_storage.upload_file(file, folder='blog/images/')
        logger.info(f"CKEditor upload successful: {url}")
        
        # CKEditor 5 expects this format
        return JsonResponse({'url': url})
    
    except (IOError, OSError) as e:
        logger.error(f"File I/O error during upload: {str(e)}")
        return JsonResponse({
            'error': {'message': 'Failed to read file. Please try again.'}
        }, status=400)
    
    except Exception as e:
        logger.exception(f"Unexpected error in CKEditor upload: {str(e)}")
        return JsonResponse({
            'error': {'message': 'Upload failed. Please try again.'}
        }, status=500)
