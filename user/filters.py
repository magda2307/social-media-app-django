import django_filters
from .models import Post

class PostFilter(django_filters.FilterSet):
    """Filter for Post object."""
    tags__name = django_filters.CharFilter(method='filter_tags__name')

    class Meta:
        model = Post
        fields = {
            'tags__name': ['exact', 'icontains'],
            'date_created': ['gte', 'lte','exact'],
            'likes': ['gte', 'lte'],
            'text': ['icontains'],
        }
        ordering_fields = ['date_created', 'likes']
    def filter_tags__name(self, queryset, name, value):
        tags = value.replace(" ", "").split(',')  # Split the tags by comma, 
        # remove all spaces

        # Filter posts that have all the specified tags
        for tag in tags:
            queryset = queryset.filter(tags__name=tag)

        return queryset.distinct()