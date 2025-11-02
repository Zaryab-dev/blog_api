# 🛒 eBay Product URL Field - Implementation

## Overview

Added `ebay_product_url` field to Post model to store eBay product links for blog posts.

## Changes Made

### 1. Model Field Added

**File:** `blog/models.py`

```python
ebay_product_url = models.URLField(max_length=500, blank=True, help_text='eBay product link')
```

**Properties:**
- Type: URLField
- Max Length: 500 characters
- Optional: Yes (blank=True)
- Validates: URL format

### 2. Serializers Updated

**Files:** `blog/serializers.py`

Added to both serializers:
- ✅ `PostListSerializer` - Returns in list view
- ✅ `PostDetailSerializer` - Returns in detail view

### 3. Admin Interface Updated

**File:** `blog/admin.py`

**Changes:**
- ✅ Added to "Advanced" fieldset
- ✅ Added to search fields
- ✅ Added "eBay" column in list view (✅/❌ indicator)

**Admin List Display:**
```
Title | Author | Status | ... | eBay | Thumbnail
Post1 | John   | Pub    | ... | ✅   | [img]
Post2 | Jane   | Draft  | ... | ❌   | [img]
```

### 4. Migration Created

**File:** `blog/migrations/0016_add_ebay_product_url.py`

## Deployment

### Step 1: Run Migration

```bash
python manage.py migrate blog
```

**Expected Output:**
```
Running migrations:
  Applying blog.0016_add_ebay_product_url... OK
```

### Step 2: Verify in Admin

1. Go to Django Admin: `/admin/blog/post/`
2. Open any post
3. Scroll to "Advanced" section
4. See "eBay product link" field

### Step 3: Test API

```bash
# List endpoint
curl https://backend.zaryableather.com/api/v1/posts/ | jq '.[0].ebay_product_url'

# Detail endpoint
curl https://backend.zaryableather.com/api/v1/posts/{slug}/ | jq '.ebay_product_url'
```

## Usage

### In Django Admin

1. Edit a post
2. Expand "Advanced" section
3. Paste eBay product URL
4. Save

**Example:**
```
https://www.ebay.com/itm/123456789
```

### Via API

**Create Post:**
```python
POST /api/v1/posts/
{
  "title": "Leather Jacket Review",
  "summary": "...",
  "content": "...",
  "ebay_product_url": "https://www.ebay.com/itm/123456789"
}
```

**Update Post:**
```python
PATCH /api/v1/posts/{slug}/
{
  "ebay_product_url": "https://www.ebay.com/itm/987654321"
}
```

### In Python

```python
from blog.models import Post

# Create post with eBay link
post = Post.objects.create(
    title="Leather Jacket",
    summary="...",
    content="...",
    ebay_product_url="https://www.ebay.com/itm/123456789"
)

# Update eBay link
post.ebay_product_url = "https://www.ebay.com/itm/new-link"
post.save()

# Check if post has eBay link
if post.ebay_product_url:
    print(f"Buy on eBay: {post.ebay_product_url}")
```

## API Response

### List View

```json
{
  "id": "uuid",
  "title": "Leather Jacket Review",
  "slug": "leather-jacket-review",
  "summary": "...",
  "ebay_product_url": "https://www.ebay.com/itm/123456789",
  "views_count": 150
}
```

### Detail View

```json
{
  "id": "uuid",
  "title": "Leather Jacket Review",
  "slug": "leather-jacket-review",
  "content_html": "<p>...</p>",
  "ebay_product_url": "https://www.ebay.com/itm/123456789",
  "product_references": [],
  "locale": "en"
}
```

## Frontend Integration

### Next.js Example

```tsx
// In your blog post component
export default function BlogPost({ post }) {
  return (
    <article>
      <h1>{post.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: post.content_html }} />
      
      {post.ebay_product_url && (
        <div className="product-cta">
          <a 
            href={post.ebay_product_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ebay"
          >
            🛒 Buy on eBay
          </a>
        </div>
      )}
    </article>
  );
}
```

### React Example

```jsx
function ProductLink({ ebayUrl }) {
  if (!ebayUrl) return null;
  
  return (
    <div className="ebay-link">
      <a href={ebayUrl} target="_blank" rel="noopener noreferrer">
        <img src="/ebay-logo.png" alt="eBay" />
        View Product on eBay
      </a>
    </div>
  );
}
```

## Validation

The field validates:
- ✅ URL format (http:// or https://)
- ✅ Max length (500 chars)
- ✅ Optional (can be empty)

**Valid Examples:**
```
https://www.ebay.com/itm/123456789
https://ebay.com/itm/product-name-123
http://www.ebay.co.uk/itm/456789
```

**Invalid Examples:**
```
not-a-url
ebay.com/item  (missing protocol)
```

## Search

The field is searchable in Django Admin:

```
Search: "ebay.com/itm/123456789"
→ Finds posts with that eBay link
```

## Filtering

Filter posts with/without eBay links:

```python
# Posts with eBay links
posts_with_ebay = Post.objects.exclude(ebay_product_url='')

# Posts without eBay links
posts_without_ebay = Post.objects.filter(ebay_product_url='')
```

## Benefits

- ✅ **Affiliate Links** - Store eBay affiliate URLs
- ✅ **Product Reviews** - Link to reviewed products
- ✅ **Monetization** - Direct product links
- ✅ **User Experience** - Easy product access
- ✅ **Tracking** - Track which posts have product links

## Future Enhancements

Potential additions:
- Amazon product URL
- Store product URL
- Multiple product URLs (JSON field)
- Affiliate tracking parameters
- Product price tracking

## Rollback

If needed, remove the field:

```bash
python manage.py migrate blog 0015_add_seo_enhancements
```

---

**Status:** ✅ Implemented
**Migration:** `0016_add_ebay_product_url`
**API:** ✅ Available in both list and detail endpoints
**Admin:** ✅ Editable with visual indicator
