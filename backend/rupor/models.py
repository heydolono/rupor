from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint
from users.models import User

class Tag(models.Model):
    """ Класс модели Тег """

    name = models.CharField(max_length=50, verbose_name='Название тега', unique=True)
    color = models.CharField(max_length=7, verbose_name='Цветовой HEX-код', unique=True)
    slug = models.SlugField(max_length=50, verbose_name='Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Blog(models.Model):
    """ Класс модели Блог """
    author = models.ForeignKey(
        User,
        related_name='blog',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Автор публикации',
    )
    name = models.CharField(max_length=100, verbose_name='Название',)
    image = models.ImageField(
        upload_to='blog/',
        null=True,  
        default=None,
        verbose_name='Текстовое описание',
    )
    text = models.TextField('Текст блога')
    tags = models.ManyToManyField(
        Tag,
        related_name='blog',
        verbose_name='Тег',
    )

    class Meta:
        verbose_name = 'Блог'
        verbose_name_plural = 'Блоги'

    def __str__(self):
        return self.name


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'blog')
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий {self.author} к {self.blog}'


class Favourite(models.Model):
    """ Класс модели Избранное """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(fields=['user', 'blog'], name='unique_favourite')
        ]

    def __str__(self):
        return f'"{self.blog}" добавлен в Избранное'
