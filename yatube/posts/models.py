from core.models import CreateModel, PubDateModel
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.constraints import UniqueConstraint

User = get_user_model()
COUNT_SYMBOL = 15


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(unique=True, verbose_name='URL-ярлык')
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name_plural = 'Группы'


class Post(PubDateModel):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Название группы',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self) -> str:
        return self.text[:COUNT_SYMBOL]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(CreateModel):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='comments',
        verbose_name='Автор'
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )

    def __str__(self) -> str:
        return self.text

    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    UniqueConstraint(fields=['user', 'author'], name='follow_unique')

    def __str__(self) -> str:
        return self.user
