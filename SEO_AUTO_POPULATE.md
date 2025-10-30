# SEO Auto-Population Feature

## Overview

Automatically generates SEO and Open Graph metadata from blog post content to ensure consistency, save time, and improve SEO performance.

---

## ✅ What Gets Auto-Populated

When you create or update a post, the following fields are automatically generated **if not manually set**:

1. **SEO Title** (`seo_title`)
2. **SEO Description** (`seo_description`)
3. **OG Title** (`og_title`)
4. **OG Description** (`og_description`)
5. **Canonical URL** (`canonical_url`)

---

## 📋 Generation Rules

### 1. SEO Title
- **Format:** `{Post Title} | {Site Name}`
- **Max Length:** 60 characters
- **Example:** `Ultimate Guide to Leather Care | Zaryab Leather Blog`
- **Logic:** If full title exceeds 60 chars, post title is truncated to fit site name

### 2. SEO Description
- **Source:** Post summary
- **Max Length:** 160 characters
- **Processing:** HTML stripped, whitespace normalized
- **Truncation:** At word boundary with "..." if needed
- **Example:** `Learn how to clean, protect, and maintain your leather goods for years of durability...`

### 3. OG Title
- **Source:** Post title (clean, no site name)
- **Max Length:** 70 characters
- **Example:** `Ultimate Guide to Leather Care and Maintenance`
- **Note:** Social platforms prefer clean titles without site branding

### 4. OG Description
- **Source:** Post summary
- **Max Length:** 200 characters
- **Processing:** Same as SEO description but allows more context
- **Example:** `Learn how to clean, protect, and maintain your leather goods with expert-backed care tips and techniques.`

### 5. Canonical URL
- **Format:** `{SITE_URL}/blog/{post-slug}`
- **Example:** `https://zaryableather.com/blog/ultimate-guide-leather-care`
- **Note:** Uses `SITE_URL` from settings

---

## 🔧 How It Works

### Automatic Generation
SEO metadata is auto-generated when you save a post:

```python
# Create a new post
post = Post.objects.create(
    title="Ultimate Guide to Leather Care",
    summary="Learn how to maintain your leather goods...",
    content_html="<p>Full content here</p>",
    author=author
)

# SEO fields are automatically populated!
print(post.seo_title)  # "Ultimate Guide to Leather Care | Zaryab Leather Blog"
print(post.og_title)   # "Ultimate Guide to Leather Care"
print(post.canonical_url)  # "https://zaryableather.com/blog/ultimate-guide-leather-care"
```

### Manual Override
You can always override auto-generated values:

```python
post = Post.objects.create(
    title="My Post",
    summary="Summary here",
    seo_title="Custom SEO Title",  # Manual override
    og_title="Custom OG Title",    # Manual override
    author=author
)

# Manual values are preserved
print(post.seo_title)  # "Custom SEO Title" (not auto-generated)
print(post.seo_description)  # Auto-generated from summary
```

---

## 📊 Example Output

### Input Post
```python
{
    "title": "Ultimate Guide to Leather Care and Maintenance",
    "summary": "Learn how to clean, protect, and maintain your leather goods for years of durability with expert-backed care tips and techniques.",
    "slug": "ultimate-guide-leather-care",
    "content_html": "<p>Full article content...</p>"
}
```

### Auto-Generated SEO Metadata
```json
{
    "seo_title": "Ultimate Guide to Leather Care and | Zaryab Leather Blog",
    "seo_description": "Learn how to clean, protect, and maintain your leather goods for years of durability with expert-backed care tips and techniques.",
    "og_title": "Ultimate Guide to Leather Care and Maintenance",
    "og_description": "Learn how to clean, protect, and maintain your leather goods for years of durability with expert-backed care tips and techniques.",
    "canonical_url": "https://zaryableather.com/blog/ultimate-guide-leather-care"
}
```

---

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python3 test_seo_auto_populate.py
```

**Expected Output:**
```
🧪 Testing SEO Auto-Population
============================================================

📝 Test 1: SEO Title Generation
✅ PASS

📝 Test 2: Meta Description Generation
✅ PASS

📝 Test 3: OG Title Generation
✅ PASS

📝 Test 4: OG Description Generation
✅ PASS

📝 Test 5: Canonical URL Generation
✅ PASS

📝 Test 6: Auto-populate on Save
✅ PASS

📝 Test 7: Manual Override Preserved
✅ PASS

🎉 All tests passed!
```

---

## ⚙️ Configuration

### Required Settings

Ensure these are set in your `settings.py` or `.env`:

```python
# Site Configuration
SITE_NAME = 'Zaryab Leather Blog'
SITE_URL = 'https://zaryableather.com'
```

### Environment Variables

```bash
# .env
SITE_NAME=Zaryab Leather Blog
SITE_URL=https://zaryableather.com
```

---

## 📝 Best Practices

### 1. Write Good Summaries
Since SEO descriptions are generated from summaries, write clear, compelling summaries:

✅ **Good:**
```
Learn how to clean, protect, and maintain your leather goods with expert-backed care tips.
```

❌ **Bad:**
```
This post is about leather care.
```

### 2. Keep Titles Concise
Shorter titles work better with auto-generation:

✅ **Good:** `Ultimate Guide to Leather Care` (32 chars)

⚠️ **Long:** `The Complete and Comprehensive Ultimate Guide to Professional Leather Care` (72 chars - will be truncated)

### 3. Manual Override When Needed
For special cases, manually set SEO fields:

```python
post.seo_title = "Buy Leather Care Products | Free Shipping"
post.og_description = "Special promotional description for social media"
```

---

## 🔍 SEO Guidelines Followed

- ✅ **Title Length:** ≤ 60 characters (Google's recommendation)
- ✅ **Description Length:** 150-160 characters (optimal for SERPs)
- ✅ **OG Title:** Clean, no site branding (social media best practice)
- ✅ **OG Description:** Up to 200 characters (Facebook/Twitter optimal)
- ✅ **Canonical URL:** Always reflects live post URL
- ✅ **HTML Stripping:** All tags removed from descriptions
- ✅ **Whitespace Normalization:** Clean, readable text
- ✅ **Word Boundary Truncation:** No mid-word cuts

---

## 📁 Files

- **`blog/seo_auto_populate.py`** - Core auto-population logic
- **`blog/models.py`** - Integration in Post.save()
- **`test_seo_auto_populate.py`** - Comprehensive test suite
- **`SEO_AUTO_POPULATE.md`** - This documentation

---

## 🎯 Benefits

1. **Consistency** - All posts have proper SEO metadata
2. **Time Saving** - No manual duplication of content
3. **SEO Optimized** - Follows Google's best practices
4. **Flexibility** - Manual override always available
5. **Automatic** - Works on every save
6. **Tested** - Comprehensive test coverage

---

## 🚀 Usage in Admin

When creating a post in Django admin:

1. Fill in **Title** and **Summary** (required)
2. Leave SEO fields blank (or fill for custom values)
3. Save the post
4. SEO metadata is automatically generated!

Check the generated values in the admin interface after saving.

---

## ✅ Success!

SEO auto-population is now active. Every post automatically gets:
- Optimized SEO title
- Compelling meta description
- Social media-ready OG tags
- Proper canonical URL

**No manual work required!** 🎉
