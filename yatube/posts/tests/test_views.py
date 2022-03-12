from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post
from posts.views import NUMBER_OF_POSTS

User = get_user_model()


class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='test-slug',
            description='Описание группы',
        )
        for i in range(1, 14):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Пост {i}',
                pub_date=f'Дата {i}',
                group=cls.group
            )
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
        cls.paginated_urls = (
            cls.index_url,
            cls.group_list_url,
            cls.profile_url
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_about_page_uses_correct_template(self):
        """URL-адреса приложения posts используют верные шаблоны"""
        templates_names_pages = (
            (reverse(self.index_url[0]), self.index_url[1]),
            (reverse(
                self.profile_url[0], args=(self.profile_url[2],)
            ), self.profile_url[1]),
            (reverse(
                self.post_detail_url[0],
                args=(self.post_detail_url[2],)
            ), self.post_detail_url[1]),
            (reverse(self.create_post_url[0]), self.create_post_url[1]),
            (reverse(
                self.edit_post_url[0],
                args=(self.edit_post_url[2],)
            ), self.edit_post_url[1]),
            (reverse(
                self.group_list_url[0],
                args=(self.group_list_url[2],)
            ), self.group_list_url[1])
        )
        for reverse_name, template in templates_names_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(self.index_url[0]))
        first_page = list(Post.objects.all()[:NUMBER_OF_POSTS])
        self.assertEqual(list(response.context['page_obj']), first_page)
        self.assertEqual(len(response.context['page_obj']), NUMBER_OF_POSTS)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                self.group_list_url[0], kwargs={'slug': self.group_list_url[2]}
            )
        )
        first_page = list(
            Post.objects.filter(group=self.group)[:NUMBER_OF_POSTS]
        )
        self.assertEqual(list(response.context['page_obj']), first_page)
        self.assertEqual(len(response.context['page_obj']), NUMBER_OF_POSTS)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                self.profile_url[0],
                kwargs={'username': self.profile_url[2]}
            )
        )
        list_posts_user = list(
            Post.objects.filter(author=self.user)[:NUMBER_OF_POSTS]
        )
        self.assertEqual(list(response.context['page_obj']), list_posts_user)
        self.assertEqual(len(response.context['page_obj']), NUMBER_OF_POSTS)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                self.post_detail_url[0],
                kwargs={'post_id': self.post_detail_url[2]}
            )
        )
        for expected in list(Post.objects.filter(id=self.post.id)):
            self.assertEqual(response.context['post_user'], expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(self.create_post_url[0]))
        expected = forms.fields.CharField
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, expected)


class PostsViewAdditionalTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Название группы',
            slug='test-slug',
            description='Описание группы',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Пост',
            pub_date='Дата',
            group=self.group
        )
        self.index_url = ('posts:index', 'posts/index.html', None)
        self.group_list_url = (
            'posts:group_list', 'posts/group_list.html', (self.group.slug)
        )

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(self.index_url[0]))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.pub_date, self.post.pub_date)
        self.assertEqual(first_object.group, self.post.group)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                self.group_list_url[0], kwargs={'slug': self.group_list_url[2]}
            )
        )
        self.assertEqual(response.context['group'].title, self.group.title)
        self.assertEqual(response.context['group'].slug, self.group.slug)
        self.assertEqual(
            response.context['group'].description, self.group.description
        )
