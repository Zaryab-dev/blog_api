"""Schema API Endpoints"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from .models import Post, Author
from .seo_schema_generator import (
    generate_blog_posting_schema,
    generate_person_schema,
    generate_organization_schema,
    generate_website_schema,
    generate_breadcrumb_schema,
    sync_schema_to_db
)


@api_view(['GET'])
@cache_page(60 * 60 * 24)
def schema_post(request, slug):
    """Get BlogPosting schema for a post"""
    post = get_object_or_404(
        Post.published.select_related('author', 'featured_image').prefetch_related('categories', 'tags'),
        slug=slug
    )
    
    schema = generate_blog_posting_schema(post)
    sync_schema_to_db(post, 'BlogPosting', schema)
    
    return Response(schema)


@api_view(['GET'])
@cache_page(60 * 60 * 24)
def schema_site(request):
    """Get Website + Organization schema"""
    website_schema = generate_website_schema()
    org_schema = generate_organization_schema()
    
    return Response({
        "@context": "https://schema.org",
        "@graph": [website_schema, org_schema]
    })


@api_view(['GET'])
@cache_page(60 * 60 * 24)
def schema_author(request, username):
    """Get Person schema for an author"""
    author = get_object_or_404(Author, slug=username)
    
    schema = generate_person_schema(author)
    sync_schema_to_db(author, 'Person', schema)
    
    return Response(schema)


@api_view(['GET'])
@cache_page(60 * 60 * 12)
def schema_breadcrumbs(request, slug):
    """Get BreadcrumbList schema for a post"""
    post = get_object_or_404(
        Post.published.prefetch_related('categories'),
        slug=slug
    )
    
    schema = generate_breadcrumb_schema(post)
    
    return Response(schema)
