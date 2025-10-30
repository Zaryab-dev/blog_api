"""
Related posts recommendation engine
"""
from django.db.models import Count, Q


def get_related_posts(post, limit=5):
    """
    Get related posts based on categories, tags, and author.
    
    Scoring:
    - Same category: +3 points per match
    - Same tag: +2 points per match
    - Same author: +1 point
    
    Returns optimized queryset with select_related and prefetch_related.
    """
    from blog.models import Post
    
    # Get post's categories and tags
    post_categories = list(post.categories.values_list('id', flat=True))
    post_tags = list(post.tags.values_list('id', flat=True))
    
    # Build query for related posts
    related = Post.published.exclude(id=post.id)
    
    # Filter by relevance
    if post_categories or post_tags:
        related = related.filter(
            Q(categories__id__in=post_categories) |
            Q(tags__id__in=post_tags) |
            Q(author=post.author)
        ).distinct()
    else:
        # Fallback: same author
        related = related.filter(author=post.author)
    
    # Annotate with match counts for scoring
    related = related.annotate(
        category_matches=Count('categories', filter=Q(categories__id__in=post_categories)),
        tag_matches=Count('tags', filter=Q(tags__id__in=post_tags))
    )
    
    # Order by relevance score, then by date
    related = related.order_by(
        '-category_matches',
        '-tag_matches',
        '-published_at'
    )
    
    # Optimize queries
    related = related.select_related('author', 'featured_image').prefetch_related('categories', 'tags')
    
    return related[:limit]
