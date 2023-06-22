import django_filters
from .models import Post
from django.db.models import Count

class PostFilter(django_filters.FilterSet):
    """Filter for Post object."""
    tags__name = django_filters.CharFilter(method='filter_tags__name')
    likes_count__gte = django_filters.NumberFilter(method='filter_likes_count__gte')
    likes_count__lte = django_filters.NumberFilter(method='filter_likes_count__lte')
    likes_count__exact = django_filters.NumberFilter(method='filter_likes_count__exact')

    class Meta:
        model = Post
        fields = {
            'tags__name': ['exact', 'icontains'],
            'date_created': ['gte', 'lte', 'exact'],
            'text': ['icontains'],
        }
        ordering_fields = ['date_created', 'likes_count']

    def filter_tags__name(self, queryset, name, value):
        tags = value.replace(" ", "").split(',')
        for tag in tags:
            queryset = queryset.filter(tags__name=tag)
        return queryset.distinct()

    def filter_likes_count__exact(self, queryset, name, value):
        try:
            value = int(value)
        except:
            return queryset.none()
            
        queryset = queryset.annotate(likes_count=Count('likes')).filter(likes_count=value)
        return queryset.distinct()

    def filter_likes_count__gte(self, queryset, name, value):
        try:
            value = int(value)
        except:
            return queryset.none()
            
        queryset = queryset.annotate(likes_count=Count('likes')).filter(likes_count__gte=value)
        return queryset.distinct()

    def filter_likes_count__lte(self, queryset, name, value):
        try:
            value = int(value)
        except:
            return queryset.none()
            
        queryset = queryset.annotate(likes_count=Count('likes')).filter(likes_count__lte=value)
        return queryset.distinct()
