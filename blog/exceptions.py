"""
Custom exceptions for the blog application
"""


class BlogAPIException(Exception):
    """Base exception for blog API"""
    pass


class ImageUploadError(BlogAPIException):
    """Raised when image upload fails"""
    pass


class StorageConnectionError(BlogAPIException):
    """Raised when Supabase connection fails"""
    pass


class InvalidContentError(BlogAPIException):
    """Raised when blog content is invalid"""
    pass


class ValidationError(BlogAPIException):
    """Raised when data validation fails"""
    pass
