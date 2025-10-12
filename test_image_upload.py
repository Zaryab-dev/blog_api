#!/usr/bin/env python
"""
Test script for image upload to Supabase
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leather_api.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from blog.models import ImageAsset
from core.storage import supabase_storage
from PIL import Image
import io

def create_test_image():
    """Create a test image in memory"""
    img = Image.new('RGB', (800, 600), color='red')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile(
        "test-image.jpg",
        img_io.read(),
        content_type="image/jpeg"
    )

def test_supabase_upload():
    """Test direct Supabase upload"""
    print("🧪 Testing Supabase Storage Upload...")
    
    try:
        # Create test image
        test_file = create_test_image()
        
        # Upload to Supabase
        url = supabase_storage.upload_file(
            test_file,
            folder='blog-images/',
            filename='test-upload'
        )
        
        print(f"✅ Upload successful!")
        print(f"📸 URL: {url}")
        return url
    
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return None

def test_image_asset_creation(url):
    """Test ImageAsset model creation"""
    print("\n🧪 Testing ImageAsset Creation...")
    
    try:
        image_asset = ImageAsset.objects.create(
            file=url,
            alt_text="Test Image",
            width=800,
            height=600,
            format='jpeg'
        )
        
        print(f"✅ ImageAsset created!")
        print(f"🆔 ID: {image_asset.id}")
        print(f"📝 Alt Text: {image_asset.alt_text}")
        print(f"📏 Dimensions: {image_asset.width}x{image_asset.height}")
        print(f"🔗 URL: {image_asset.file}")
        
        return image_asset
    
    except Exception as e:
        print(f"❌ ImageAsset creation failed: {str(e)}")
        return None

def main():
    print("=" * 60)
    print("🚀 Image Upload Test Suite")
    print("=" * 60)
    
    # Test 1: Supabase upload
    url = test_supabase_upload()
    
    if url:
        # Test 2: ImageAsset creation
        image_asset = test_image_asset_creation(url)
        
        if image_asset:
            print("\n" + "=" * 60)
            print("✅ All tests passed!")
            print("=" * 60)
            print("\n📋 Summary:")
            print(f"   - Supabase upload: ✅")
            print(f"   - ImageAsset creation: ✅")
            print(f"   - Image URL: {url}")
            print(f"   - Database ID: {image_asset.id}")
        else:
            print("\n❌ ImageAsset creation failed")
    else:
        print("\n❌ Supabase upload failed")

if __name__ == '__main__':
    main()
