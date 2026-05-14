from django.contrib import admin
from django.contrib.admin import display

from .models import (Favourite, Blog, Tag, Like, Comment)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'moderation_status', 'added_in_favorites',)
    readonly_fields = ('added_in_favorites',)
    list_filter = ('author', 'name', 'tags', 'moderation_status',)
    actions = ['approve_posts']

    @display(description='Общее число добавлений этого блога в избранное')
    def added_in_favorites(self, obj):
        return obj.favorites.count()

    @admin.action(description='Разблокировать выбранные посты')
    def approve_posts(self, request, queryset):
        updated = queryset.update(moderation_status='approved')
        self.message_user(request, f'Разблокировано {updated} постов')


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
    list_display = ('author', 'blog', 'moderation_status', 'created_at', 'updated_at')
    list_filter = ('author', 'blog', 'created_at', 'moderation_status')
    search_fields = ('text', 'author__username', 'blog__name')
    actions = ['approve_comments']

    @admin.action(description='Разблокировать выбранные комментарии')
    def approve_comments(self, request, queryset):
        updated = queryset.update(moderation_status='approved')
        self.message_user(request, f'Разблокировано {updated} комментариев')