from posts.forms import PostForm, CommentForm
from django.test import Client, TestCase, override_settings
from posts.models import Post, Group, Comment, Follow
from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus
import tempfile
import shutil
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Kokuriko')
        cls.user_2 = User.objects.create_user(username='NewAuthor')
        cls.user_following = User.objects.create_user(username='Following')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='test-slug',
            description='Описание группы',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост',
            pub_date='12.12.12',
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            text='Комментарий-1',
            post=cls.post,
            author=cls.user
        )
        cls.follow = Follow.objects.create(
            author=cls.user_following,
            user=cls.user
        )
        cls.form = PostForm()
        cls.form_comments = CommentForm()

        post_args = cls.post.id
        cls.index_url = ('posts:index', 'posts/index.html', None)
        cls.group_list_url = (
            'posts:group_list', 'posts/group_list.html', (cls.group.slug)
        )
        cls.profile_url = (
            'posts:profile', 'posts/profile.html', (cls.user.username)
        )
        cls.post_detail_url = (
            'posts:post_detail', 'posts/post_detail.html', (post_args)
        )
        cls.create_post_url = (
            'posts:post_create', 'posts/create_post.html', None
        )
        cls.edit_post_url = (
            'posts:post_edit', 'posts/create_post.html', (post_args)
        )
        cls.add_comment_url = (
            'posts:add_comment', 'posts/post_detail.html', (post_args)
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в create"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост с картинкой',
        }
        response = self.authorized_client.post(
            reverse(self.create_post_url[0]),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse(
                             self.profile_url[0],
                             kwargs={'username': self.profile_url[2]})
                             )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Валидная форма изменяет запись в edit"""
        posts_count = Post.objects.count()
        form_data = {'text': 'Отредактированная запись'}
        response = self.authorized_client.post(
            reverse(
                self.edit_post_url[0],
                kwargs={'post_id': self.edit_post_url[2]}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(text='Отредактированная запись').exists()
        )
        self.assertRedirects(
            response, reverse(
                self.post_detail_url[0],
                kwargs={'post_id': self.post_detail_url[2]}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauth_user_cant_publish_post(self):
        """Неавторизованный пользователь не может создать пост."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Пост от неавторизованного пользователя'}
        response = self.guest_client.post(
            reverse(self.create_post_url[0]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertNotIn(
            Post.objects.filter(
                text='Пост от неавторизованного пользователя'
            ), Post.objects.all()
        )

    def test_image_on_pages(self):
        """Картинка появилась на страницах"""
        response_detail = self.authorized_client.get(
            reverse(
                self.post_detail_url[0],
                kwargs={'post_id': self.post_detail_url[2]}
            )
        )
        response_index = self.authorized_client.get(
            reverse(self.index_url[0])
        )
        response_group_list = self.authorized_client.get(
            reverse(
                self.group_list_url[0],
                kwargs={'slug': self.group_list_url[2]}
            )
        )
        response_profile = self.authorized_client.get(
            reverse(
                self.profile_url[0],
                kwargs={'username': self.profile_url[2]}
            )
        )
        page_detail = response_detail.context['post_user']
        page_index = response_index.context['page_obj'][0]
        page_group_list = response_group_list.context['page_obj'][0]
        page_profile = response_profile.context['page_obj'][0]
        self.assertEqual(page_detail.image, self.post.image)
        self.assertEqual(page_index.image, self.post.image)
        self.assertEqual(page_group_list.image, self.post.image)
        self.assertEqual(page_profile.image, self.post.image)

    def test_comments_on_post_detail(self):
        """Появился новый комментарий"""
        comment_count = Comment.objects.count()
        form_data = {'text': 'Комментарий-2'}
        response = self.authorized_client.post(
            reverse(
                self.add_comment_url[0],
                kwargs={'post_id': self.add_comment_url[2]}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(text='Комментарий-2').exists()
        )
        self.assertRedirects(
            response, reverse(
                self.post_detail_url[0],
                kwargs={'post_id': self.post_detail_url[2]}
            )
        )

    def test_follow_authorized_client(self):
        """Подписка авторизованного пользователя на других авторов"""
        follow_count_user = (
            Follow.objects.
            filter(user=self.user).
            values_list('author_id', flat=True).
            count()
        )
        follow_count_user_following = (
            Follow.objects.
            filter(user=self.user_following).
            values_list('author_id', flat=True).
            count()
        )
        form_data = {
            'author': self.user_2,
            'user': self.user
        }
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_2.username}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Follow.objects.
            filter(user=self.user).
            values_list('author_id', flat=True).
            count(),
            follow_count_user + 1
        )
        self.assertEqual(
            Follow.objects.
            filter(user=self.user_following).
            values_list('author_id', flat=True).
            count(),
            follow_count_user_following
        )

    def test_follow_delete(self):
        """Отписка авторизованного пользователя от других авторов"""
        follow = Follow.objects.filter(
            user=self.user, author=self.user_following
        )
        follow.delete()
        self.assertEqual(
            Follow.objects.
            filter(user=self.user).
            values_list('author_id', flat=True).
            count(),
            0
        )
    
    def test_cache_index(self):
        """Данные сохраняются в кэше"""
        response_first = self.authorized_client.get(
            reverse(self.index_url[0])
        )
        self.post.delete()
        response_second = self.authorized_client.get(
            reverse(self.index_url[0])
        )
        self.assertEqual(response_first.content, response_second.content)