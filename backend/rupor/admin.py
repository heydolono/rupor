from django.contrib import admin
from django.contrib.admin import display

from .models import (Favourite, Blog, Tag, Like, Comment)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'added_in_favorites',)
    readonly_fields = ('added_in_favorites',)
    list_filter = ('author', 'name', 'tags',)

    @display(description='Общее число добавлений этого блога в избранное')
    def added_in_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog',)
    list_filter = ('user', 'blog',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'blog', 'created_at', 'updated_at')
    list_filter = ('author', 'blog', 'created_at')
    search_fields = ('text', 'author__username', 'blog__name')