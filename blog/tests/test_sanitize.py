"""
Tests for HTML sanitization utilities
"""
import pytest
from django.test import TestCase
from blog.utils_sanitize import (
    sanitize_html, strip_html_tags, calculate_reading_time,
    extract_excerpt, count_words
)


class SanitizeTestCase(TestCase):
    """Test HTML sanitization"""
    
    def test_sanitize_removes_script_tags(self):
        """Test that script tags are removed"""
        html = '<p>Hello</p><script>alert("xss")</script>'
        result = sanitize_html(html)
        self.assertNotIn('<script>', result)
        self.assertIn('<p>Hello</p>', result)
    
    def test_sanitize_allows_safe_tags(self):
        """Test that safe tags are preserved"""
        html = '<p>Hello <strong>world</strong></p>'
        result = sanitize_html(html)
        self.assertEqual(result, html)
    
    def test_sanitize_removes_dangerous_attributes(self):
        """Test that dangerous attributes are removed"""
        html = '<p onclick="alert()">Hello</p>'
        result = sanitize_html(html)
        self.assertNotIn('onclick', result)
    
    def test_sanitize_preserves_images(self):
        """Test that images are preserved"""
        html = '<img src="test.jpg" alt="Test" />'
        result = sanitize_html(html)
        self.assertIn('<img', result)
        self.assertIn('src="test.jpg"', result)
    
    def test_strip_html_tags(self):
        """Test stripping HTML tags"""
        html = '<p>Hello <strong>world</strong></p>'
        result = strip_html_tags(html)
        self.assertEqual(result, 'Hello world')
    
    def test_strip_html_with_nested_tags(self):
        """Test stripping nested HTML tags"""
        html = '<div><p>Hello</p><p>World</p></div>'
        result = strip_html_tags(html)
        self.assertEqual(result, 'Hello World')
    
    def test_calculate_reading_time(self):
        """Test reading time calculation"""
        # 200 words = 1 minute
        html = '<p>' + ' '.join(['word'] * 200) + '</p>'
        result = calculate_reading_time(html)
        self.assertEqual(result, 1)
        
        # 400 words = 2 minutes
        html = '<p>' + ' '.join(['word'] * 400) + '</p>'
        result = calculate_reading_time(html)
        self.assertEqual(result, 2)
    
    def test_calculate_reading_time_minimum(self):
        """Test minimum reading time is 1 minute"""
        html = '<p>Short text</p>'
        result = calculate_reading_time(html)
        self.assertEqual(result, 1)
    
    def test_extract_excerpt(self):
        """Test excerpt extraction"""
        html = '<p>' + 'word ' * 100 + '</p>'
        result = extract_excerpt(html, max_length=50)
        self.assertLessEqual(len(result), 53)  # 50 + "..."
        self.assertTrue(result.endswith('...'))
    
    def test_extract_excerpt_short_text(self):
        """Test excerpt with short text"""
        html = '<p>Short text</p>'
        result = extract_excerpt(html, max_length=100)
        self.assertEqual(result, 'Short text')
        self.assertFalse(result.endswith('...'))
    
    def test_count_words(self):
        """Test word counting"""
        html = '<p>Hello world this is a test</p>'
        result = count_words(html)
        self.assertEqual(result, 6)
    
    def test_count_words_with_tags(self):
        """Test word counting ignores tags"""
        html = '<p>Hello <strong>world</strong></p>'
        result = count_words(html)
        self.assertEqual(result, 2)
    
    def test_sanitize_empty_content(self):
        """Test sanitizing empty content"""
        result = sanitize_html('')
        self.assertEqual(result, '')
        
        result = sanitize_html(None)
        self.assertEqual(result, '')
