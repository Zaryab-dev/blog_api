# Category Filtering Implementation

## ✅ Updated Category API

The categories endpoint now supports filtering by specific slugs, allowing the frontend to fetch only selected categories.

## API Usage

### Get All Categories
```bash
GET /api/v1/categories/
```

Returns all categories with post counts.

### Get Specific Categories by Slug
```bash
GET /api/v1/categories/?slugs=leather-care,fashion-tips,product-reviews
```

Returns only the categories with slugs: `leather-care`, `fashion-tips`, and `product-reviews`.

### Get Single Category
```bash
GET /api/v1/categories/{slug}/
```

Returns a single category by its slug.

## Frontend Implementation

### Example: Fetch Selected Categories

```javascript
// Next.js example
const selectedSlugs = ['leather-care', 'fashion-tips', 'product-reviews'];
const slugsParam = selectedSlugs.join(',');

const response = await fetch(
  `https://backend.zaryableather.com/api/v1/categories/?slugs=${slugsParam}`
);
const categories = await response.json();
```

### Example: React Component

```jsx
import { useEffect, useState } from 'react';

function CategoryNav() {
  const [categories, setCategories] = useState([]);
  
  // Define which categories to display
  const displayCategories = ['leather-care', 'fashion-tips', 'product-reviews'];
  
  useEffect(() => {
    const fetchCategories = async () => {
      const slugs = displayCategories.join(',');
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/categories/?slugs=${slugs}`
      );
      const data = await res.json();
      setCategories(data);
    };
    
    fetchCategories();
  }, []);
  
  return (
    <nav>
      {categories.map(cat => (
        <a key={cat.slug} href={`/category/${cat.slug}`}>
          {cat.name} ({cat.count_published_posts})
        </a>
      ))}
    </nav>
  );
}
```

## Response Format

```json
[
  {
    "id": "uuid",
    "name": "Leather Care",
    "slug": "leather-care",
    "description": "Tips and guides for leather maintenance",
    "count_published_posts": 15
  },
  {
    "id": "uuid",
    "name": "Fashion Tips",
    "slug": "fashion-tips",
    "description": "Latest fashion trends and styling advice",
    "count_published_posts": 23
  }
]
```

## Benefits

1. **Performance**: Fetch only needed categories, reducing payload size
2. **Control**: Frontend controls which categories to display
3. **Flexibility**: Easy to add/remove categories without backend changes
4. **Caching**: Responses are cached for 1 hour (3600 seconds)

## Implementation Details

### Backend Changes

Updated `CategoryViewSet` in `blog/views.py`:

```python
def get_queryset(self):
    queryset = super().get_queryset()
    slugs = self.request.query_params.get('slugs', '').strip()
    if slugs:
        slug_list = [s.strip() for s in slugs.split(',') if s.strip()]
        queryset = queryset.filter(slug__in=slug_list)
    return queryset
```

### Query Parameters

- **Parameter**: `slugs`
- **Format**: Comma-separated list of category slugs
- **Example**: `?slugs=leather-care,fashion-tips`
- **Optional**: If not provided, returns all categories

## Testing

```bash
# Test all categories
curl https://backend.zaryableather.com/api/v1/categories/

# Test filtered categories
curl "https://backend.zaryableather.com/api/v1/categories/?slugs=leather-care,fashion-tips"

# Test single category
curl https://backend.zaryableather.com/api/v1/categories/leather-care/
```

## Deployment Status

- ✅ Code updated
- ✅ Deployed to Elastic Beanstalk
- ✅ Environment: django-blog-api-prod
- ✅ Status: Healthy

---

**Updated**: October 30, 2025  
**Deployed**: Yes  
**Environment**: Production
