import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import CommentForm, PostForm
from posts.models import Comment, Group, Post, User

USERNAME = 'author'
GROUP_TITLE = 'Тестовое сообщество'
SLUG = 'test_group'
GROUP_DESCRIPTION = 'Тестовое описание группы'
GROUP_TITLE_2 = 'Тестовое сообщество 2'
SLUG_2 = 'test_group_2'
GROUP_DESCRIPTION_2 = 'Тестовое описание группы 2'
POST_TEXT = 'Тестовая публикация'
POST_TEXT_2 = 'Тестовая публикация 2'
EDITED_TEXT = 'Редактируем текст поста'
COMMENT_TEXT_1 = 'Это комментарий 1'
COMMENT_TEXT_2 = 'А это ещё комментарий'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
LOGIN_URL = reverse('login')
LOGIN_NEW_POST_URL = f'{LOGIN_URL}?next={NEW_POST_URL}'
IMAGE_CONTENT = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
IMAGE_NAME = 'image.gif'
IMAGE_NAME_2 = 'image2.gif'
IMAGE = SimpleUploadedFile(
    name=IMAGE_NAME,
    content=IMAGE_CONTENT,
    content_type='image/gif'
)
IMAGE_2 = SimpleUploadedFile(
    name=IMAGE_NAME_2,
    content=IMAGE_CONTENT,
    content_type='image/gif'
)
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.author = User.objects.create_user(USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.group_2 = Group.objects.create(
            title=GROUP_TITLE_2,
            slug=SLUG_2,
            description=GROUP_DESCRIPTION_2
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.author,
            group=cls.group,
        )
        cls.POST_URL = reverse('post', args=[
            PostFormTests.author, PostFormTests.post.id
        ])
        cls.POST_EDIT_URL = reverse('post_edit', args=[
            PostFormTests.author, PostFormTests.post.id
        ])
        cls.LOGIN_POST_EDIT_URL = f'{LOGIN_URL}?next={cls.POST_EDIT_URL}'
        cls.guest_client = Client()
        cls.author_authorized_client = Client()
        cls.author_authorized_client.force_login(cls.author)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """Валидная форма поста создает запись в базе данных."""
        posts_id = tuple(Post.objects.all().values_list('id', flat=True))
        posts_count = len(posts_id)
        form_data = {
            'text': POST_TEXT_2,
            'group': self.group.id,
            'image': IMAGE,
        }
        response = self.author_authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        page = response.context['page']
        for i in range(len(page)):
            if page[i].id not in posts_id:
                new_post = page[i]
        self.assertRedirects(response, INDEX_URL)
        self.assertEqual(
            len(page), posts_count + 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(new_post.author, self.author)
        self.assertEqual(
            new_post.image,
            f"{settings.UPLOAD_FOLDER}{form_data['image'].name}"
        )

    def test_edit_post(self):
        """При редактировании поста изменяется соответствующая запись"""
        post_count = Post.objects.count()
        form_edit_data = {
            'text': EDITED_TEXT,
            'group': self.group_2.id,
            'image': IMAGE_2,
        }
        response = self.author_authorized_client.post(
            self.POST_EDIT_URL, data=form_edit_data, follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        updadted_post = response.context['post']
        self.assertEqual(
            updadted_post.text,
            form_edit_data['text']
        )
        self.assertEqual(
            updadted_post.group.id,
            form_edit_data['group']
        )
        self.assertEqual(
            updadted_post.author,
            self.post.author
        )
        self.assertEqual(
            updadted_post.image,
            f"{settings.UPLOAD_FOLDER}{form_edit_data['image'].name}"
        )

    def test_guest_cant_create_post(self):
        """Гость не может создать пост"""
        posts_count = Post.objects.count()
        form_data = {
            'text': POST_TEXT_2,
        }
        response = self.guest_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertFalse(
            Post.objects.filter(text=POST_TEXT_2).exists()
        )
        self.assertRedirects(
            response,
            LOGIN_NEW_POST_URL
        )
        self.assertEqual(
            Post.objects.count(), posts_count)

    def test_guest_cant_edit_post(self):
        """Гость не может редактировать пост"""
        form_edit_data = {
            'text': EDITED_TEXT,
        }
        response = self.guest_client.post(
            self.POST_EDIT_URL, data=form_edit_data, follow=True
        )
        self.assertFalse(
            Post.objects.filter(text=EDITED_TEXT).exists()
        )
        self.assertRedirects(
            response,
            self.LOGIN_POST_EDIT_URL
        )

    def test_new_post_shows_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        urls = [NEW_POST_URL, self.POST_EDIT_URL]
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.author_authorized_client.get(url)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CommentForm()
        cls.author = User.objects.create_user(USERNAME)
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.author,
        )
        cls.comment = Comment.objects.create(
            text=COMMENT_TEXT_1,
            author=cls.author,
            post=cls.post,
        )
        cls.POST_URL = reverse('post', args=[
            CommentFormTests.author, CommentFormTests.post.id
        ])
        cls.ADD_COMMENT_URL = reverse('add_comment', args=[
            CommentFormTests.author, CommentFormTests.post.id
        ])
        cls.LOGIN_COMMENT_URL = f'{LOGIN_URL}?next={cls.ADD_COMMENT_URL}'
        cls.guest_client = Client()
        cls.author_authorized_client = Client()
        cls.author_authorized_client.force_login(cls.author)

    def test_create_comment(self):
        """Валидная форма комментария создает запись в базе данных."""
        comments_id = tuple(Comment.objects.all().values_list('id', flat=True))
        comments_count = len(comments_id)
        form_data = {
            'text': COMMENT_TEXT_2,
            'post': self.post.id,
        }
        response = self.author_authorized_client.post(
            self.ADD_COMMENT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_URL)
        comments = response.context['comments']
        for i in range(len(comments)):
            if comments[i].id not in comments_id:
                new_comment = comments[i]
        self.assertEqual(
            len(comments), comments_count + 1)
        self.assertEqual(new_comment.text, form_data['text'])
        self.assertEqual(new_comment.author, self.author)
        self.assertEqual(new_comment.post, self.post)

    def test_comment_shows_correct_context(self):
        """Шаблон comment сформирован с правильным контекстом."""
        form_fields = {
            'text': forms.CharField,
        }
        response = self.author_authorized_client.get(self.POST_URL)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_guest_cant_comment(self):
        """Гость не может комментировать"""
        form_data = {
            'text': COMMENT_TEXT_2,
            'post': self.post.id,
        }
        response = self.guest_client.post(
            self.ADD_COMMENT_URL,
            data=form_data,
            follow=True
        )
        self.assertFalse(
            Comment.objects.filter(
                post=self.post.id,
                text=COMMENT_TEXT_2
            ).exists()
        )
        self.assertRedirects(
            response,
            self.LOGIN_COMMENT_URL
        )
