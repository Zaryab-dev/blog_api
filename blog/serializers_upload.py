"""
Custom serializers for handling Supabase uploads
"""
from rest_framework import serializers
from .models import ImageAsset, Post
from core.storage import supabase_storage
import logging

logger = logging.getLogger(__name__)


class ImageAssetUploadSerializer(serializers.ModelSerializer):
    """Serializer for ImageAsset with Supabase upload"""
    file = serializers.ImageField(write_only=True, required=False)
    url = serializers.URLField(source='file', read_only=True)
    
    class Meta:
        model = ImageAsset
        fields = ['id', 'file', 'url', 'alt_text', 'width', 'height', 'format']
    
    def create(self, validated_data):
        file = validated_data.pop('file', None)
        
        if file:
            # Upload to Supabase
            try:
                # Use alt_text or filename for SEO-friendly name
                filename = validated_data.get('alt_text') or file.name
                url = supabase_storage.upload_file(
                    file, 
                    folder='blog-images/',
                    filename=filename
                )
                validated_data['file'] = url
                logger.info(f"✅ Image uploaded to Supabase: {url}")
            except Exception as e:
                logger.error(f"❌ Supabase upload failed: {str(e)}")
                raise serializers.ValidationError(f"Image upload failed: {str(e)}")
        
        return super().create(validated_data)


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for Post create/update with featured_image upload"""
    featured_image_file = serializers.ImageField(write_only=True, required=False)
    featured_image_url = serializers.URLField(source='featured_image.file', read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'summary', 'content',
            'author', 'categories', 'tags',
            'featured_image', 'featured_image_file', 'featured_image_url',
            'status', 'published_at', 'seo_title', 'seo_description'
        ]
        read_only_fields = ['id', 'slug']
    
    def create(self, validated_data):
        featured_image_file = validated_data.pop('featured_image_file', None)
        
        if featured_image_file:
            # Upload to Supabase with SEO-friendly filename
            try:
                title = validated_data.get('title', 'image')
                url = supabase_storage.upload_file(
                    featured_image_file,
                    folder='blog-images/',
                    filename=title
                )
                
                # Create ImageAsset with Supabase URL
                image_asset = ImageAsset.objects.create(
                    file=url,
                    alt_text=f"{title} featured image",
                    format=featured_image_file.content_type.split('/')[-1]
                )
                validated_data['featured_image'] = image_asset
                logger.info(f"✅ Featured image uploaded: {url}")
            except Exception as e:
                logger.error(f"❌ Featured image upload failed: {str(e)}")
                raise serializers.ValidationError(f"Featured image upload failed: {str(e)}")
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        featured_image_file = validated_data.pop('featured_image_file', None)
        
        if featured_image_file:
            # Upload new image to Supabase
            try:
                title = validated_data.get('title', instance.title)
                url = supabase_storage.upload_file(
                    featured_image_file,
                    folder='blog-images/',
                    filename=title
                )
                
                # Update or create ImageAsset
                if instance.featured_image:
                    instance.featured_image.file = url
                    instance.featured_image.save()
                else:
                    image_asset = ImageAsset.objects.create(
                        file=url,
                        alt_text=f"{title} featured image",
                        format=featured_image_file.content_type.split('/')[-1]
                    )
                    validated_data['featured_image'] = image_asset
                
                logger.info(f"✅ Featured image updated: {url}")
            except Exception as e:
                logger.error(f"❌ Featured image update failed: {str(e)}")
                raise serializers.ValidationError(f"Featured image update failed: {str(e)}")
        
        return super().update(instance, validated_data)
