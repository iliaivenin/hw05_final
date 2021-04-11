from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


USERNAME = 'author'
SLUG = 'test_group'
POST_TEXT = 'Тестовая публикация'
GROUP_TITLE = 'Тестовое сообщество'
GROUP_DESCRIPTION = 'Тестовое описание группы'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
GROUP_URL = reverse('group_posts', args=[SLUG])
PROFILE_URL = reverse('profile', args=[USERNAME])
LOGIN_URL = reverse('login')
LOGIN_NEW_POST_URL = f'{LOGIN_URL}?next={NEW_POST_URL}'
PAGE_404 = '/page/not/found'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(USERNAME)
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.author,
            group=cls.group,
        )
        cls.POST_EDIT_URL = reverse('post_edit', args=[
            cls.author, cls.post.id
        ])
        cls.POST_URL = reverse('post', args=[
            cls.author, cls.post.id
        ])

    def setUp(self):
        # неавторизованный клиент
        self.guest_client = Client()
        # авторизованный клиент для автора записи
        self.author_authorized_client = Client()
        self.author_authorized_client.force_login(self.author)
        # авторизованный клиент для другого пользователя
        self.user_authorized_client = Client()
        self.user_authorized_client.force_login(self.user)

    def test_responses(self):
        """Проверка кодов возврата"""
        responses = [
            [INDEX_URL, self.guest_client, 200],
            [GROUP_URL, self.guest_client, 200],
            [PROFILE_URL, self.guest_client, 200],
            [self.POST_URL, self.guest_client, 200],
            [NEW_POST_URL, self.user_authorized_client, 200],
            [self.POST_EDIT_URL, self.author_authorized_client, 200],
            [self.POST_EDIT_URL, self.user_authorized_client, 302],
            [self.POST_EDIT_URL, self.guest_client, 302],
            [NEW_POST_URL, self.guest_client, 302],
            [PAGE_404, self.guest_client, 404],
        ]
        for url, client, code in responses:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, code)

    def test_redirects(self):
        """Проверка перенаправлений"""
        redirects = [
            ([NEW_POST_URL, self.guest_client, LOGIN_NEW_POST_URL]),
            [self.POST_EDIT_URL, self.guest_client, self.POST_URL],
            [self.POST_EDIT_URL, self.user_authorized_client, self.POST_URL],
        ]
        for url_in, client, url_out in redirects:
            with self.subTest(url_in=url_in):
                self.assertRedirects(
                    client.get(url_in, follow=True),
                    url_out
                )

    def test_pages_use_correct_templates(self):
        """Проверка шаблонов"""
        templates = [
            [INDEX_URL, self.guest_client, 'index.html'],
            [GROUP_URL, self.guest_client, 'group.html'],
            [NEW_POST_URL, self.user_authorized_client, 'new.html'],
            [PROFILE_URL, self.guest_client, 'profile.html'],
            [self.POST_URL, self.user_authorized_client, 'post.html'],
            [self.POST_EDIT_URL, self.author_authorized_client, 'new.html'],
        ]
        for url, client, template in templates:
            with self.subTest(url=url):
                self.assertTemplateUsed(client.get(url), template)
