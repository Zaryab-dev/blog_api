"""
Custom admin widgets for Supabase image uploads
"""
from django import forms
from django.utils.safestring import mark_safe
from core.storage import supabase_storage
import logging

logger = logging.getLogger(__name__)


class SupabaseImageWidget(forms.ClearableFileInput):
    """
    Custom widget for uploading images to Supabase in Django admin
    """
    template_name = 'admin/widgets/supabase_image.html'
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs = attrs or {}
        self.attrs.update({'accept': 'image/*'})
    
    def render(self, name, value, attrs=None, renderer=None):
        """Render widget with preview if image exists"""
        html = super().render(name, value, attrs, renderer)
        
        if value and isinstance(value, str):
            # value is the Supabase URL
            preview_html = f'''
            <div style="margin-top: 10px;">
                <img src="{value}" style="max-width: 300px; max-height: 300px; border: 1px solid #ddd; padding: 5px;" />
                <p style="margin-top: 5px; color: #666; font-size: 12px;">Current image</p>
            </div>
            '''
            html = preview_html + html
        
        return mark_safe(html)
