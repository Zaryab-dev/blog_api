#!/usr/bin/env python
"""
Test script for Supabase upload functionality
Run: python test_supabase_upload.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leather_api.settings')
django.setup()

from core.storage import supabase_storage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def test_supabase_connection():
    """Test Supabase client initialization"""
    print("Testing Supabase connection...")
    try:
        print(f"✓ Supabase URL: {supabase_storage.url}")
        print(f"✓ Bucket: {supabase_storage.bucket}")
        print("✓ Client initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def test_upload():
    """Test file upload to Supabase"""
    print("\nTesting file upload...")
    try:
        # Create a dummy image file
        content = b"fake image content for testing"
        file = InMemoryUploadedFile(
            file=BytesIO(content),
            field_name='upload',
            name='test.jpg',
            content_type='image/jpeg',
            size=len(content),
            charset=None
        )
        
        # Upload
        url = supabase_storage.upload_file(file, folder='test/')
        print(f"✓ Upload successful: {url}")
        return url
    except Exception as e:
        print(f"✗ Upload failed: {e}")
        return None

def test_public_url():
    """Test public URL generation"""
    print("\nTesting public URL generation...")
    try:
        url = supabase_storage.get_public_url('test/example.jpg')
        print(f"✓ Public URL: {url}")
        return True
    except Exception as e:
        print(f"✗ URL generation failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Supabase Upload Test Suite")
    print("=" * 60)
    
    results = []
    results.append(("Connection", test_supabase_connection()))
    results.append(("Public URL", test_public_url()))
    results.append(("Upload", test_upload() is not None))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed."))
