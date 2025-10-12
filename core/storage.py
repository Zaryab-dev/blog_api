"""
Supabase Storage utility for file uploads
"""
from supabase import create_client, Client
from django.conf import settings
from django.utils.text import slugify
import uuid
from pathlib import Path
import time


class SupabaseStorage:
    """Handle file uploads to Supabase Storage using official client"""
    
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.api_key = settings.SUPABASE_API_KEY
        self.bucket = settings.SUPABASE_BUCKET
        self.client: Client = create_client(self.url, self.api_key)
    
    def upload_file(self, file, folder="uploads/", filename=None):
        """
        Upload file to Supabase Storage
        
        Args:
            file: Django UploadedFile object
            folder: Destination folder in bucket
            filename: Optional custom filename (will be slugified)
            
        Returns:
            str: Public URL of uploaded file
        """
        # Generate filename
        ext = Path(file.name).suffix.lower()
        if filename:
            base_name = slugify(filename)
            filename = f"{base_name}-{int(time.time())}{ext}"
        else:
            filename = f"{uuid.uuid4()}{ext}"
        
        path = f"{folder}{filename}"
        
        # Read file content
        file.seek(0)
        file_content = file.read()
        
        # Upload to Supabase
        self.client.storage.from_(self.bucket).upload(
            path=path,
            file=file_content,
            file_options={"content-type": file.content_type or "application/octet-stream"}
        )
        
        # Return public URL
        return self.get_public_url(path)
    
    def get_public_url(self, path):
        """Get public URL for uploaded file"""
        return self.client.storage.from_(self.bucket).get_public_url(path)
    
    def delete_file(self, path):
        """Delete file from Supabase Storage"""
        try:
            self.client.storage.from_(self.bucket).remove([path])
            return True
        except Exception:
            return False


# Singleton instance
supabase_storage = SupabaseStorage()
