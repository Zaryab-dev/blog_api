"""
Custom admin forms for Supabase uploads
"""
from django import forms
from .models import ImageAsset
from core.storage import supabase_storage
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class ImageAssetAdminForm(forms.ModelForm):
    """
    Custom form for ImageAsset that uploads to Supabase
    """
    upload_file = forms.ImageField(
        required=False,
        label='Upload Image',
        help_text='Upload image to Supabase Storage (JPEG, PNG, GIF, WebP - Max 10MB)'
    )
    
    class Meta:
        model = ImageAsset
        fields = ['upload_file', 'file', 'alt_text', 'width', 'height', 'format']
        widgets = {
            'file': forms.TextInput(attrs={'readonly': 'readonly', 'size': 80}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = False
        self.fields['file'].help_text = 'Supabase URL (auto-generated after upload)'
    
    def clean(self):
        cleaned_data = super().clean()
        upload_file = cleaned_data.get('upload_file')
        file_url = cleaned_data.get('file')
        
        # If uploading new file
        if upload_file:
            # Validate file size (max 10MB)
            if upload_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File too large. Maximum size is 10MB.')
            
            try:
                # Get image dimensions
                image = Image.open(upload_file)
                width, height = image.size
                format_type = image.format.lower() if image.format else 'unknown'
                
                # Reset file pointer
                upload_file.seek(0)
                
                # Upload to Supabase
                alt_text = cleaned_data.get('alt_text', upload_file.name)
                url = supabase_storage.upload_file(
                    upload_file,
                    folder='blog-images/',
                    filename=alt_text
                )
                
                # Update cleaned data
                cleaned_data['file'] = url
                cleaned_data['width'] = width
                cleaned_data['height'] = height
                cleaned_data['format'] = format_type
                
                logger.info(f"✅ Image uploaded to Supabase: {url}")
                
            except Exception as e:
                logger.error(f"❌ Supabase upload failed: {str(e)}")
                raise forms.ValidationError(f'Upload failed: {str(e)}')
        
        # Ensure file URL exists
        elif not file_url:
            raise forms.ValidationError('Please upload an image or provide a Supabase URL.')
        
        return cleaned_data
