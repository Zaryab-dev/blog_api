#!/usr/bin/env python3
"""
Test SEO auto-population functionality
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leather_api.settings')
django.setup()

from blog.models import Post, Author
from blog.seo_auto_populate import (
    generate_seo_title,
    generate_meta_description,
    generate_og_title,
    generate_og_description,
    generate_canonical_url
)


def test_seo_generation():
    """Test SEO metadata generation"""
    print("\n🧪 Testing SEO Auto-Population")
    print("=" * 60)
    
    # Create test author
    author, _ = Author.objects.get_or_create(
        name="Test Author",
        defaults={'slug': 'test-author'}
    )
    
    # Create test post
    post = Post(
        title="Ultimate Guide to Leather Care and Maintenance",
        slug="ultimate-guide-leather-care",
        summary="Learn how to clean, protect, and maintain your leather goods for years of durability with expert-backed care tips and techniques.",
        content_html="<p>Test content</p>",
        author=author
    )
    
    # Test 1: SEO Title
    print("\n📝 Test 1: SEO Title Generation")
    seo_title = generate_seo_title(post)
    print(f"Generated: {seo_title}")
    print(f"Length: {len(seo_title)} chars")
    assert len(seo_title) <= 60, "SEO title too long"
    assert "Zaryab Leather Blog" in seo_title, "Site name missing"
    print("✅ PASS")
    
    # Test 2: Meta Description
    print("\n📝 Test 2: Meta Description Generation")
    meta_desc = generate_meta_description(post)
    print(f"Generated: {meta_desc}")
    print(f"Length: {len(meta_desc)} chars")
    assert len(meta_desc) <= 160, "Meta description too long"
    assert "..." in meta_desc or len(post.summary) <= 160, "Truncation issue"
    print("✅ PASS")
    
    # Test 3: OG Title
    print("\n📝 Test 3: OG Title Generation")
    og_title = generate_og_title(post)
    print(f"Generated: {og_title}")
    print(f"Length: {len(og_title)} chars")
    assert len(og_title) <= 70, "OG title too long"
    assert "Zaryab Leather Blog" not in og_title, "Site name should not be in OG title"
    print("✅ PASS")
    
    # Test 4: OG Description
    print("\n📝 Test 4: OG Description Generation")
    og_desc = generate_og_description(post)
    print(f"Generated: {og_desc}")
    print(f"Length: {len(og_desc)} chars")
    assert len(og_desc) <= 200, "OG description too long"
    print("✅ PASS")
    
    # Test 5: Canonical URL
    print("\n📝 Test 5: Canonical URL Generation")
    canonical = generate_canonical_url(post)
    print(f"Generated: {canonical}")
    assert post.slug in canonical, "Slug missing from canonical URL"
    assert canonical.startswith("http"), "Invalid URL format"
    print("✅ PASS")
    
    # Test 6: Auto-populate on save
    print("\n📝 Test 6: Auto-populate on Save")
    post.save()
    
    print(f"SEO Title: {post.seo_title}")
    print(f"SEO Description: {post.seo_description}")
    print(f"OG Title: {post.og_title}")
    print(f"OG Description: {post.og_description}")
    print(f"Canonical URL: {post.canonical_url}")
    
    assert post.seo_title, "SEO title not populated"
    assert post.seo_description, "SEO description not populated"
    assert post.og_title, "OG title not populated"
    assert post.og_description, "OG description not populated"
    assert post.canonical_url, "Canonical URL not populated"
    print("✅ PASS")
    
    # Test 7: Manual override preserved
    print("\n📝 Test 7: Manual Override Preserved")
    post2 = Post.objects.create(
        title="Another Test Post",
        slug="another-test-post",
        summary="Test summary",
        content_html="<p>Content</p>",
        author=author,
        seo_title="Custom SEO Title",
        og_title="Custom OG Title"
    )
    
    assert post2.seo_title == "Custom SEO Title", "Manual SEO title overridden"
    assert post2.og_title == "Custom OG Title", "Manual OG title overridden"
    assert post2.seo_description, "Auto-populated fields missing"
    print("✅ PASS")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    Post.objects.filter(slug__in=['ultimate-guide-leather-care', 'another-test-post']).delete()
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_seo_generation()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
