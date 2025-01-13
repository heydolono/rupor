from django_filters.rest_framework import FilterSet, filters
from rupor.models import Blog, Like


class BlogFilter(FilterSet):
    tags = filters.CharFilter(field_name='tags__slug') 
    author = filters.CharFilter(field_name='author__id')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_liked = filters.BooleanFilter(method='filter_is_liked')

    class Meta:
        model = Blog
        fields = ('tags', 'author',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorites__user=user)
        return queryset
    
    def filter_is_liked(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(likes__user=user)
        return queryset