from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            pub_date='Дата',
            group=cls.group
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        def_str = {
            str(post): post.text,
            str(group): group.title
        }
        for key, value in def_str.items():
            with self.subTest(key=key):
                self.assertEqual(def_str[key], value)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Название группы',
            'pub_date': 'Дата создания'
        }
        for key, value in field_verboses.items():
            with self.subTest(key=key):
                self.assertEqual(post._meta.get_field(key).verbose_name, value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for key, value in field_help_text.items():
            with self.subTest(key=key):
                self.assertEqual(post._meta.get_field(key).help_text, value)
