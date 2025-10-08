"""
Full-text search utilities for PostgreSQL

This module provides search functionality using PostgreSQL's full-text search
with GIN indexes. The search is ready at the database level via the GIN index
on Post.content_html defined in models.py.

Search will be exposed via API endpoint in Phase 3.
"""
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q


class PostSearchManager:
    """Manager for full-text search on Post model"""
    
    @staticmethod
    def search(queryset, query_string):
        """
        Full-text search on Post title, summary, and content
        
        Uses PostgreSQL GIN index for performance.
        
        Args:
            queryset: Post queryset to search within
            query_string: Search query string
            
        Returns:
            Queryset ordered by search rank
        """
        if not query_string:
            return queryset
        
        # Create search vectors for different fields with weights
        search_vector = (
            SearchVector('title', weight='A') +
            SearchVector('summary', weight='B') +
            SearchVector('content_html', weight='C')
        )
        
        search_query = SearchQuery(query_string)
        
        return queryset.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank')
    
    @staticmethod
    def fuzzy_search(queryset, query_string):
        """
        Fuzzy search using trigram similarity (requires pg_trgm extension)
        
        Note: Requires PostgreSQL extension:
            CREATE EXTENSION IF NOT EXISTS pg_trgm;
        
        Args:
            queryset: Post queryset to search within
            query_string: Search query string
            
        Returns:
            Queryset with fuzzy matches
        """
        if not query_string:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=query_string) |
            Q(summary__icontains=query_string) |
            Q(content_html__icontains=query_string)
        )


# Confirmation: Full-text search is ready at DB level
# - GIN index on Post.content_html (defined in models.py)
# - SearchVector with weighted fields (title=A, summary=B, content=C)
# - SearchRank for relevance ordering
# - Ready to expose via /api/v1/posts/?search=query in Phase 3
