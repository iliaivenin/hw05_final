import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User


USERNAME = 'author'
POST_TEXT = 'Тестовая публикация'
POST_TEXT_2 = 'Очень уникальный текст, который нигде не повторяется'
SLUG_1 = 'test_group_1'
GROUP_TITLE_1 = 'Тестовое сообщество 1'
GROUP_DESCRIPTION_1 = 'Тестовое описание группы 1'
GROUP_URL_1 = reverse('group_posts', args=[SLUG_1])
SLUG_2 = 'test_group_2'
GROUP_TITLE_2 = 'Тестовое сообщество 2'
GROUP_DESCRIPTION_2 = 'Тестовое описание группы 2'
GROUP_URL_2 = reverse('group_posts', args=[SLUG_2])
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
PROFILE_URL = reverse('profile', args=[USERNAME])
FOLLOW_URL = reverse('follow_index')
PROFILE_FOLLOW_URL = reverse('profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse('profile_unfollow', args=[USERNAME])
IMAGE = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
FILE_NAME = 'image.gif'
file = SimpleUploadedFile(
    name=FILE_NAME,
    content=IMAGE,
    content_type='image/gif'
)
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(USERNAME)
        cls.user = User.objects.create_user(username='user')
        cls.group_1 = Group.objects.create(
            title=GROUP_TITLE_1,
            slug=SLUG_1,
            description=GROUP_DESCRIPTION_1
        )
        cls.group_2 = Group.objects.create(
            title=GROUP_TITLE_2,
            slug=SLUG_2,
            description=GROUP_DESCRIPTION_2
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.author,
            group=cls.group_1,
            image=file
        )
        cls.POST_URL = reverse('post', args=[
            cls.author, cls.post.id
        ])
        cls.POST_EDIT_URL = reverse('post_edit', args=[
            cls.author, cls.post.id
        ])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.author_authorized_client = Client()
        self.author_authorized_client.force_login(self.author)
        self.user_authorized_client = Client()
        self.user_authorized_client.force_login(self.user)

    def test_context(self):
        """Шаблоны страниц сформированы с правильным контекстом."""
        Follow.objects.create(
            author=self.author,
            user=self.user
        )
        urls = [INDEX_URL, PROFILE_URL, GROUP_URL_1, self.POST_URL, FOLLOW_URL]
        for url in urls:
            with self.subTest(url=url):
                response = self.user_authorized_client.get(url)
                if 'page' in response.context:
                    self.assertEqual(len(response.context['page']), 1)
                    post = response.context['page'][0]
                else:
                    post = response.context['post']
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(
                    post.author,
                    self.post.author
                )
                self.assertEqual(post.group, self.group_1)
                self.assertEqual(
                    post.image,
                    f'{settings.UPLOAD_FOLDER}{FILE_NAME}'
                )

    def test_post_not_in_group_2(self):
        """Созданный пост не попал в чужую группу"""
        response = self.author_authorized_client.get(GROUP_URL_2)
        self.assertNotIn(self.post, response.context['page'])

    def test_author(self):
        """Шаблоны страниц с правильным автором"""
        urls = [PROFILE_URL, self.POST_URL]
        for url in urls:
            with self.subTest(url=url):
                response = self.author_authorized_client.get(url)
                self.assertEqual(response.context['author'].username, USERNAME)

    def test_new_post_creates_new_post(self):
        """Главная страница кэширует информацию"""
        response = self.guest_client.get(INDEX_URL)
        Post.objects.create(
            text=POST_TEXT_2,
            author=self.author,
            group=self.group_1
        )
        response_after_adding_post = self.guest_client.get(INDEX_URL)
        self.assertEqual(
            response.content,
            response_after_adding_post.content
        )
        cache.clear()
        response_after_cache_clear = self.guest_client.get(INDEX_URL)
        self.assertNotEqual(
            response.content,
            response_after_cache_clear.content
        )

    def test_authorized_user_can_follow(self):
        """Возможность подписываться на других пользователей"""
        self.user_authorized_client.get(PROFILE_FOLLOW_URL)
        self.assertTrue(
            Follow.objects.filter(
                author=self.author,
                user=self.user
            ).exists()
        )

    def test_authorized_user_can_unfollow(self):
        """Возможность отписываться от других пользователей"""
        Follow.objects.create(
            author=self.author,
            user=self.user
        )
        self.user_authorized_client.get(PROFILE_UNFOLLOW_URL)
        self.assertFalse(
            Follow.objects.filter(
                author=self.author,
                user=self.user
            ).exists()
        )

    def test_subscribed_user_can_see_following(self):
        """Пост автора виден в ленте follow подписавшегося пользователя"""
        Follow.objects.create(
            author=self.author,
            user=self.user
        )
        response = self.user_authorized_client.get(FOLLOW_URL)
        self.assertIn(self.post, response.context['page'])

    def test_not_subscribed_user_can_not_see_following(self):
        """Пост автора не виден в ленте follow неподписавшегося пользователя"""
        response = self.author_authorized_client.get(FOLLOW_URL)
        self.assertNotIn(self.post, response.context['page'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.DELTA = 3
        cls.test_user = User.objects.create(username='user')
        Post.objects.bulk_create([Post(
            text=f'Тестовая публикация{i}',
            author=cls.test_user)
            for i in range(cls.DELTA + settings.POSTS_PER_PAGE)]
        )

    def test_first_page(self):
        """Тест paginator 1-я страница"""
        self.assertEqual(
            len(self.client.get(INDEX_URL).context['page']),
            settings.POSTS_PER_PAGE
        )

    def test_second_page(self):
        """Тест paginator 2-я страница"""
        self.assertEqual(
            len(self.client.get(f'{INDEX_URL}?page=2').context['page']),
            self.DELTA
        )
