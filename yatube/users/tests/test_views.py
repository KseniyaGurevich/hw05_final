from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='noname',
            first_name='имя',
            last_name='фамилия',
            email='noname@mail.com'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_correct_namespace_name(self):
        """Проверка namespace:name"""
        templates_names_pages = {
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse('users:signup'): 'users/signup.html',
        }
        for reverse_name, template in templates_names_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_page_show_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('users:signup'))
        self.assertEqual(
            response.context.get('user').first_name, self.user.first_name
        )
        self.assertEqual(
            response.context.get('user').last_name, self.user.last_name
        )
        self.assertEqual(response.context.get('user').email, self.user.email)
