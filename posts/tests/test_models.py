from django.test import TestCase

from posts.models import Group, Post, User


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое сообщество',
            description='Тестовое описание'
        )

    def test_verbose_name_group(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'title': 'название сообщества',
            'description': 'описание',
            'slug': 'ключ',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Group._meta.get_field(value).verbose_name,
                    expected
                )

    def test_help_text_group(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'title': 'введите уникальное название сообщества',
            'description': 'описание сообщества',
            'slug': 'ключ',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Group._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild(self):
        """Функция __str__ объекта group возвращает значение group.title."""
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(self.group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        test_author = User.objects.create_user(username='TestUser')
        test_group = Group.objects.create(title='TestGroup')
        cls.post = Post.objects.create(
            text='Тестовая публикация',
            author=test_author,
            group=test_group,
        )

    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'ваш текст',
            'author': 'автор',
            'group': 'сообщество',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).verbose_name, expected)

    def test_help_text_post(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'введите текст записи',
            'author': 'выберите автора из выпадающего списка',
            'group': 'можно выбрать сообщество',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild(self):
        """Функция __str__ объекта post возвращает верный результат."""
        expected = (f'Текст: {self.post.text[:15]} | '
                    f'автор: {self.post.author.username} | '
                    f'сообщество: {self.post.group} | '
                    f'дата публикации: {self.post.pub_date:%d.%m.%Y %H:%M}')
        self.assertEqual(expected, str(self.post))
