"""Response compression middleware"""
from django.middleware.gzip import GZipMiddleware


class CompressionMiddleware(GZipMiddleware):
    """Enhanced compression with better defaults"""
    pass
