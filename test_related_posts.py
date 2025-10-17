#!/usr/bin/env python3
"""Test related posts functionality"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leather_api.settings')
django.setup()

from blog.models import Post, Author, Category, Tag
from blog.related_posts import get_related_posts


def test_related_posts():
    print("\n🧪 Testing Related Posts Engine")
    print("=" * 60)
    
    # Create test data
    author = Author.objects.get_or_create(name="Test Author", defaults={'slug': 'test-author'})[0]
    cat1 = Category.objects.get_or_create(name="Leather Care", defaults={'slug': 'leather-care'})[0]
    cat2 = Category.objects.get_or_create(name="Fashion", defaults={'slug': 'fashion'})[0]
    tag1 = Tag.objects.get_or_create(name="Maintenance", defaults={'slug': 'maintenance'})[0]
    tag2 = Tag.objects.get_or_create(name="Tips", defaults={'slug': 'tips'})[0]
    
    # Create main post
    main_post = Post.objects.create(
        title="Main Post",
        slug="main-post",
        summary="Main post summary",
        content_html="<p>Content</p>",
        author=author,
        status='published'
    )
    main_post.categories.add(cat1)
    main_post.tags.add(tag1, tag2)
    
    # Create related posts
    related1 = Post.objects.create(
        title="Related Post 1 - Same Category",
        slug="related-1",
        summary="Summary",
        content_html="<p>Content</p>",
        author=author,
        status='published'
    )
    related1.categories.add(cat1)
    
    related2 = Post.objects.create(
        title="Related Post 2 - Same Tag",
        slug="related-2",
        summary="Summary",
        content_html="<p>Content</p>",
        author=author,
        status='published'
    )
    related2.tags.add(tag1)
    
    related3 = Post.objects.create(
        title="Related Post 3 - Same Author",
        slug="related-3",
        summary="Summary",
        content_html="<p>Content</p>",
        author=author,
        status='published'
    )
    
    unrelated = Post.objects.create(
        title="Unrelated Post",
        slug="unrelated",
        summary="Summary",
        content_html="<p>Content</p>",
        author=Author.objects.get_or_create(name="Other", defaults={'slug': 'other'})[0],
        status='published'
    )
    
    # Test
    print("\n📝 Test: Get Related Posts")
    related = get_related_posts(main_post, limit=5)
    
    print(f"Found {related.count()} related posts")
    for post in related:
        print(f"  - {post.title}")
    
    assert related.count() >= 2, "Should find at least 2 related posts"
    assert main_post not in related, "Should exclude current post"
    assert unrelated not in related, "Should exclude unrelated posts"
    
    print("✅ PASS")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    Post.objects.filter(slug__in=['main-post', 'related-1', 'related-2', 'related-3', 'unrelated']).delete()
    
    print("\n🎉 All tests passed!")


if __name__ == '__main__':
    try:
        test_related_posts()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
