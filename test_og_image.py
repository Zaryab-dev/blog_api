#!/usr/bin/env python3
"""
Simple test script to verify OG image auto-population functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leather_api.settings')
django.setup()

from blog.models import Post, Author, ImageAsset

def test_og_image_functionality():
    """Test the computed_og_image property"""
    print("🧪 Testing OG Image Auto-Population")
    print("=" * 50)

    # Create test author
    author, created = Author.objects.get_or_create(
        name="Test Author",
        defaults={'slug': 'test-author'}
    )
    print(f"✅ Author: {author.name}")

    # Create test image
    image, created = ImageAsset.objects.get_or_create(
        file="https://supabase.co/storage/test.jpg",
        defaults={
            'alt_text': 'Test Image',
            'og_image_url': 'https://supabase.co/storage/og-test.jpg',
            'width': 1200,
            'height': 630,
            'format': 'jpg'
        }
    )
    print(f"✅ Image: {image.file}")

    # Test 1: Post with featured image, no manual og_image
    print("\n📸 Test 1: Featured image only")
    post1 = Post.objects.create(
        title="Test Post 1",
        summary="Summary 1",
        content_html="<p>Content 1</p>",
        author=author,
        featured_image=image
    )

    computed_og = post1.computed_og_image
    expected = "https://supabase.co/storage/og-test.jpg"
    print(f"Expected: {expected}")
    print(f"Got:      {computed_og}")
    print("✅ PASS" if computed_og == expected else "❌ FAIL")

    # Test 2: Post with manual og_image (should override)
    print("\n📝 Test 2: Manual OG image override")
    post2 = Post.objects.create(
        title="Test Post 2",
        summary="Summary 2",
        content_html="<p>Content 2</p>",
        author=author,
        featured_image=image,
        og_image="https://custom-og.com/image.jpg"
    )

    computed_og = post2.computed_og_image
    expected = "https://custom-og.com/image.jpg"
    print(f"Expected: {expected}")
    print(f"Got:      {computed_og}")
    print("✅ PASS" if computed_og == expected else "❌ FAIL")

    # Test 3: Post with no images
    print("\n🚫 Test 3: No images")
    post3 = Post.objects.create(
        title="Test Post 3",
        summary="Summary 3",
        content_html="<p>Content 3</p>",
        author=author
    )

    computed_og = post3.computed_og_image
    expected = None
    print(f"Expected: {expected}")
    print(f"Got:      {computed_og}")
    print("✅ PASS" if computed_og == expected else "❌ FAIL")

    # Test 4: Post with empty manual og_image (should use featured)
    print("\n📝 Test 4: Empty manual OG image")
    post4 = Post.objects.create(
        title="Test Post 4",
        summary="Summary 4",
        content_html="<p>Content 4</p>",
        author=author,
        featured_image=image,
        og_image="   "  # Whitespace only
    )

    computed_og = post4.computed_og_image
    expected = "https://supabase.co/storage/og-test.jpg"
    print(f"Expected: {expected}")
    print(f"Got:      {computed_og}")
    print("✅ PASS" if computed_og == expected else "❌ FAIL")

    # Cleanup
    print("\n🧹 Cleaning up test data...")
    Post.objects.filter(title__startswith="Test Post").delete()
    print("✅ Cleanup complete")

    print("\n🎉 All tests completed!")

if __name__ == '__main__':
    test_og_image_functionality()