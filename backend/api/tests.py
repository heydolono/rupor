from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from api.serializers import BlogPostSerializer, BlogSerializer
from api.serializers import SubscribeSerializer
from api.views import BlogViewSet
from rupor.models import Blog, Comment, Tag
from users.models import User


class AiBlogRegressionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.author = User.objects.create_user(
            email='author@example.com',
            username='author',
            password='password',
        )
        self.reader = User.objects.create_user(
            email='reader@example.com',
            username='reader',
            password='password',
        )
        self.tag = Tag.objects.create(
            name='Новости',
            color='#123456',
            slug='news',
        )
        self.blog = Blog.objects.create(
            author=self.author,
            name='Первый пост',
            text='Исходный текст',
            moderation_status='approved',
        )
        self.blog.tags.set([self.tag])

    @patch('api.serializers.SemanticSearchService.compute_embedding')
    @patch('api.serializers.ModerationService.moderate_blog')
    def test_partial_update_reruns_ai_and_preserves_tags(
        self,
        moderate_blog,
        compute_embedding,
    ):
        moderate_blog.return_value = {
            'moderation_status': 'approved',
            'moderation_reason': None,
        }
        compute_embedding.return_value = [0.1, 0.2, 0.3]
        request = self.factory.patch('/api/blog/1/')
        force_authenticate(request, user=self.author)

        serializer = BlogPostSerializer(
            instance=self.blog,
            data={'text': 'Обновленный текст'},
            partial=True,
            context={'request': request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.text, 'Обновленный текст')
        self.assertEqual(list(updated.tags.all()), [self.tag])
        self.assertEqual(updated.moderation_status, 'approved')
        self.assertEqual(updated.embedding, [0.1, 0.2, 0.3])
        moderate_blog.assert_called_once()
        compute_embedding.assert_called_once_with(
            title='Первый пост',
            text='Обновленный текст',
        )
        moderate_blog.assert_called_once_with(
            text='Первый пост\nОбновленный текст',
            image_file=self.blog.image,
        )

    def test_comment_count_ignores_blocked_comments(self):
        Comment.objects.create(
            author=self.reader,
            blog=self.blog,
            text='Обычный комментарий',
            moderation_status='approved',
        )
        Comment.objects.create(
            author=self.reader,
            blog=self.blog,
            text='Скрытый комментарий',
            moderation_status='blocked',
        )
        request = self.factory.get('/api/blog/1/')
        request.user = self.reader
        serializer = BlogSerializer(self.blog, context={'request': request})

        self.assertEqual(serializer.data['comments_count'], 1)

    def test_blocked_foreign_blog_is_hidden_from_detail_actions(self):
        self.blog.moderation_status = 'blocked'
        self.blog.save(update_fields=['moderation_status'])
        request = self.factory.post(
            f'/api/blog/{self.blog.id}/comment/',
            {'text': 'Комментарий'},
            format='json',
        )
        force_authenticate(request, user=self.reader)
        view = BlogViewSet.as_view({'post': 'add_comment'})

        response = view(request, pk=self.blog.id)

        self.assertEqual(response.status_code, 404)

    def test_reader_can_get_approved_blog_comments(self):
        Comment.objects.create(
            author=self.reader,
            blog=self.blog,
            text='Обычный комментарий',
            moderation_status='approved',
        )
        request = self.factory.get(f'/api/blog/{self.blog.id}/comments/')
        force_authenticate(request, user=self.reader)
        view = BlogViewSet.as_view({'get': 'get_comments'})

        response = view(request, pk=self.blog.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_subscription_serializer_hides_blocked_author_blogs(self):
        blocked_blog = Blog.objects.create(
            author=self.author,
            name='Скрытый пост',
            text='Текст',
            moderation_status='blocked',
        )
        blocked_blog.tags.set([self.tag])
        request = self.factory.get('/api/users/subscriptions/')
        request.user = self.reader

        data = SubscribeSerializer(
            self.author,
            context={'request': request},
        ).data

        self.assertEqual(data['blog_count'], 1)
        self.assertEqual([item['id'] for item in data['blog']], [self.blog.id])
