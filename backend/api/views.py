from rupor.models import Favourite, Blog, Tag, Like, Comment
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .filters import BlogFilter
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (BlogSerializer, BlogShortSerializer, BlogPostSerializer, TagSerializer, FavoriteCreateSerializer, CommentSerializer, LikeCreateSerializer)
from moderation.services import TagSuggestionService, SemanticSearchService

class BlogViewSet(ModelViewSet):
    queryset = Blog.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BlogFilter

    def get_queryset(self):
        qs = Blog.objects.all()
        user = self.request.user
        if user.is_staff:
            return qs
        if user.is_authenticated:
            return (
                qs.filter(
                    moderation_status='approved'
                ) | qs.filter(
                    author=user
                )
            ).distinct()
        return qs.filter(moderation_status='approved')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        self.request.user.save()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return BlogSerializer
        return BlogPostSerializer

    @action(detail=True, methods=['post', 'delete'], url_path='favorite',
            url_name='favorite', permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        if request.method == 'POST':
            serializer = FavoriteCreateSerializer(data={'blog': pk}, context={'request': request})
            if Favourite.objects.filter(user=request.user, blog__id=pk).exists():
                return Response({'errors': 'Блог уже был добавлен'}, status=status.HTTP_400_BAD_REQUEST)
            blog = self.get_object()
            Favourite.objects.create(user=request.user, blog=blog)
            serializerrec = BlogShortSerializer(blog)
            return Response(serializerrec.data, status=status.HTTP_201_CREATED)
        else:
            serializer = FavoriteCreateSerializer(data={'blog': pk}, context={'request': request})
            obj = Favourite.objects.filter(user=request.user, blog__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Блог уже был удален'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post', 'delete'], url_path='like', url_name='like', permission_classes=[IsAuthenticated])
    def like(self, request, pk):
        blog = self.get_object()
        if request.method == 'POST':
            serializer = LikeCreateSerializer(data={'blog': pk}, context={'request': request})
            if Like.objects.filter(user=request.user, blog__id=pk).exists():
                return Response({'errors': 'Вы уже лайкнули'}, status=status.HTTP_400_BAD_REQUEST)
            Like.objects.create(user=request.user, blog=blog)
            serializerrec = BlogShortSerializer(blog)
            return Response(serializerrec.data, status=status.HTTP_201_CREATED)
        else:
            serializer = LikeCreateSerializer(data={'blog': pk}, context={'request': request})
            like = Like.objects.filter(user=request.user, blog__id=pk)
            if like.exists():
                like.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Вы уже убрали лайк'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='comments', url_name='comments', permission_classes=[IsAuthorOrReadOnly])
    def get_comments(self, request, pk):
        blog = self.get_object()
        comments = blog.comments.all()
        if not request.user.is_staff:
            comments = comments.filter(moderation_status='approved')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='comment', url_name='comment', permission_classes=[IsAuthenticated])
    def add_comment(self, request, pk):
        serializer = CommentSerializer(data={'text': request.data.get('text'), 'blog': pk}, context={'request': request})
        blog = self.get_object()
        if serializer.is_valid():
            serializer.save(author=request.user, blog=blog)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['get'], url_path='similar',
            url_name='similar', permission_classes=[IsAuthorOrReadOnly])
    def similar(self, request, pk):
        blog = self.get_object()
        similar_blogs = SemanticSearchService.find_similar(blog, request=request)
        serializer = BlogSerializer(similar_blogs, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='suggest_tags',
            url_name='suggest_tags', permission_classes=[IsAuthenticated])
    def suggest_tags(self, request):
        title = request.data.get('name', '')
        text = request.data.get('text', '')
        suggestions = TagSuggestionService.suggest(title=title, text=text)
        return Response({'tags': suggestions}, status=status.HTTP_200_OK)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    pagination_class = None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    

class TagListView(APIView):
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)
