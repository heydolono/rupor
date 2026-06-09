import base64
from django.db import transaction
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from rupor.models import (
    Tag, Blog, Comment, Like, Favourite)
from users.models import (
    User, Subscribe
)
from users.validators import validate_username
from moderation.services import ModerationService, SemanticSearchService


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password',)
        lookup_field = 'username'

    def validate_username(self, value):
        return validate_username(value)


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj).exists()


class SubscribeSerializer(CustomUserSerializer):
    blog = serializers.SerializerMethodField()
    blog_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('blog_count', 'blog')
        read_only_fields = ('email', 'username')

    def _get_visible_blog_queryset(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        blog = obj.blog.all()
        if user and (user.is_staff or user == obj):
            return blog
        return blog.filter(moderation_status='approved')

    def get_blog(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('blog_limit')
        blog = self._get_visible_blog_queryset(obj)
        if limit:
            blog = blog[:int(limit)]
        serializer = BlogShortSerializer(blog, many=True, read_only=True)
        return serializer.data

    def get_blog_count(self, obj):
        return self._get_visible_blog_queryset(obj).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class BlogSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = (
            'id',
            'tags',
            'author',
            'is_favorited',
            'is_liked',
            'name',
            'image',
            'text',
            'likes_count',
            'comments_count',
            'moderation_status',
            'moderation_reason',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        return (
            user is not None
            and user.is_authenticated
            and Favourite.objects.filter(user=user, blog=obj).exists()
        )
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        return (
            user is not None
            and user.is_authenticated
            and Like.objects.filter(user=user, blog=obj).exists()
        )

    def get_likes_count(self, obj):
        return Like.objects.filter(blog=obj).count()

    def get_comments_count(self, obj):
        return Comment.objects.filter(
            blog=obj,
            moderation_status='approved',
        ).count()

class BlogPostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Blog
        fields = (
            'id',
            'tags',
            'author',
            'name',
            'image',
            'text',
            'moderation_status',
            'moderation_reason',
            'embedding',
        )
        read_only_fields = ('moderation_status', 'moderation_reason', 'embedding')

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise serializers.ValidationError({'tags': 'Нужно выбрать тег'})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({'tags': 'Тег не должен повторяться'})
            tags_list.append(tag)
        return value

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        image_file = validated_data.get('image')
        text = validated_data.get('text', '')
        name = validated_data.get('name', '')
        moderation_result = ModerationService.moderate_blog(
            text=f'{name}\n{text}', image_file=image_file
        )
        validated_data['moderation_status'] = moderation_result['moderation_status']
        validated_data['moderation_reason'] = moderation_result['moderation_reason']
        validated_data['embedding'] = SemanticSearchService.compute_embedding(
            title=name, text=text
        )
        blog = Blog.objects.create(**validated_data)
        blog.tags.set(tags)
        return blog

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        name = validated_data.get('name', instance.name)
        text = validated_data.get('text', instance.text)
        image_file = validated_data.get('image', instance.image)
        moderation_result = ModerationService.moderate_blog(
            text=f'{name}\n{text}', image_file=image_file
        )
        validated_data['moderation_status'] = moderation_result['moderation_status']
        validated_data['moderation_reason'] = moderation_result['moderation_reason']
        validated_data['embedding'] = SemanticSearchService.compute_embedding(
            title=name, text=text
        )
        instance = super().update(instance, validated_data)
        if tags is not None:
            instance.tags.set(tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return BlogSerializer(instance, context=context).data

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    blog = serializers.PrimaryKeyRelatedField(queryset=Blog.objects.all())

    class Meta:
        model = Comment
        fields = (
            'id', 'author', 'text', 'created_at', 'updated_at', 'blog',
            'moderation_status', 'moderation_reason',
        )
        read_only_fields = ('created_at', 'updated_at', 'moderation_status', 'moderation_reason')

    def create(self, validated_data):
        text = validated_data.get('text', '')
        moderation_result = ModerationService.moderate_comment(text=text)
        validated_data['moderation_status'] = moderation_result['moderation_status']
        validated_data['moderation_reason'] = moderation_result['moderation_reason']
        return Comment.objects.create(**validated_data)


class BlogShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Blog
        fields = ('id', 'name', 'image')


class FavoriteCreateSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    blog = serializers.PrimaryKeyRelatedField(queryset=Blog.objects.all())

    class Meta:
        model = Favourite
        fields = ('user', 'blog')

    def validate(self, attrs):
        user = self.context['request'].user
        blog = attrs['blog']
        if self.context['request'].method == 'POST':
            if Favourite.objects.filter(user=user, blog=blog).exists():
                raise serializers.ValidationError('Блог уже добавлен в избранное')
        elif self.context['request'].method == 'DELETE':
            if not Favourite.objects.filter(user=user, blog=blog).exists():
                raise serializers.ValidationError(
                    'Блог уже удален из избранного'
                )
        return attrs

    def create(self, validated_data):
        return Favourite.objects.create(**validated_data)
    

class LikeCreateSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    blog = serializers.PrimaryKeyRelatedField(queryset=Blog.objects.all())

    class Meta:
        model = Like
        fields = ('user', 'blog')

    def validate(self, attrs):
        user = self.context['request'].user
        blog = attrs['blog']
        if self.context['request'].method == 'POST':
            if Like.objects.filter(user=user, blog=blog).exists():
                raise serializers.ValidationError('Лайк поставлен')
        elif self.context['request'].method == 'DELETE':
            if not Like.objects.filter(user=user, blog=blog).exists():
                raise serializers.ValidationError(
                    'Лайк удален'
                )
        return attrs

    def create(self, validated_data):
        return Like.objects.create(**validated_data)
