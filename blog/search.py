"""
Full-text search utilities

Provides database-agnostic search with PostgreSQL optimization when available.
"""
from django.db.models import Q
from django.conf import settings


class PostSearchManager:
    """Manager for full-text search on Post model"""
    
    @staticmethod
    def search(queryset, query_string):
        """
        Full-text search on Post title, summary, and content
        
        Uses PostgreSQL GIN index when available, basic search otherwise.
        
        Args:
            queryset: Post queryset to search within
            query_string: Search query string
            
        Returns:
            Queryset ordered by relevance
        """
        if not query_string:
            return queryset
        
        # Check if using PostgreSQL
        db_engine = settings.DATABASES['default']['ENGINE']
        
        if 'postgresql' in db_engine:
            try:
                from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
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
            except:
                pass
        
        # Fallback to basic search
        return PostSearchManager.fuzzy_search(queryset, query_string)
    
    @staticmethod
    def fuzzy_search(queryset, query_string):
        """
        Basic search using LIKE queries (works on all databases)
        
        Args:
            queryset: Post queryset to search within
            query_string: Search query string
            
        Returns:
            Queryset with matches
        """
        if not query_string:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=query_string) |
            Q(summary__icontains=query_string) |
            Q(content_html__icontains=query_string)
        ).distinct()
