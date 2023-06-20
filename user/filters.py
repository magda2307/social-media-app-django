import django_filters
from .models import Post


class PostFilter(django_filters.FilterSet):
    """Filter for Post object."""
    
    def filter_by_tags(self, queryset, name, value):
        """Custom method that allows to filter posts by more than one tag. 
        It splits the provided value into individual tags, 
        assuming they are comma-separated."""
        tags = value.split(',')
        return queryset.filter(tags__name__in=tags)
        
        
    class Meta:
        model = Post
        fields = {
            'tags__name': ['exact', 'icontains'],
            'date_created': ['gte', 'lte','exact'],
            'likes': ['gte', 'lte'],
            'text': ['icontains'],
        }
        ordering_fields = ['date_created', 'likes']