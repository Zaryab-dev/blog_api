"""
Tests for CKEditor image upload functionality
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock


class ImageUploadTestCase(TestCase):
    """Test image upload to Supabase"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.upload_url = '/api/v1/upload-image/'
    
    def test_upload_requires_authentication(self):
        """Test that upload requires authentication"""
        response = self.client.post(self.upload_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('blog.views_upload.supabase_storage.upload_file')
    def test_upload_image_success(self, mock_upload):
        """Test successful image upload"""
        # Mock Supabase response
        mock_upload.return_value = 'https://supabase.co/storage/test.jpg'
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        # Create test image
        image = SimpleUploadedFile(
            "test.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        response = self.client.post(
            self.upload_url,
            {'upload': image},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uploaded'], 1)
        self.assertIn('url', response.data)
        self.assertEqual(response.data['url'], 'https://supabase.co/storage/test.jpg')
    
    def test_upload_without_file(self):
        """Test upload without file"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(self.upload_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        self.client.force_authenticate(user=self.user)
        
        # Create test file (not an image)
        file = SimpleUploadedFile(
            "test.txt",
            b"fake text content",
            content_type="text/plain"
        )
        
        response = self.client.post(
            self.upload_url,
            {'upload': file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_upload_file_too_large(self):
        """Test upload with file exceeding size limit"""
        self.client.force_authenticate(user=self.user)
        
        # Create large file (> 5MB)
        large_content = b"x" * (6 * 1024 * 1024)
        image = SimpleUploadedFile(
            "large.jpg",
            large_content,
            content_type="image/jpeg"
        )
        
        response = self.client.post(
            self.upload_url,
            {'upload': image},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('blog.views_upload.supabase_storage.upload_file')
    def test_upload_supabase_error(self, mock_upload):
        """Test handling of Supabase upload error"""
        # Mock Supabase error
        mock_upload.side_effect = Exception('Supabase error')
        
        self.client.force_authenticate(user=self.user)
        
        image = SimpleUploadedFile(
            "test.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        response = self.client.post(
            self.upload_url,
            {'upload': image},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['uploaded'], 0)
