from django.test import TestCase
from django.urls import reverse

from posts.models import Post, User


USERNAME = 'author'
SLUG = 'test_group'
POST_TEXT = 'Тестовая публикация'


class RouteTests(TestCase):
    def test_routes(self):
        """Проверка маршрутов"""
        author = User.objects.create_user(USERNAME)
        # group = Group.objects.create(slug=SLUG)
        post = Post.objects.create(text=POST_TEXT, author=author,)
        routes_reverse_names = [
            ['/', reverse('index')],
            ['/new/', reverse('new_post')],
            ['/follow/', reverse('follow_index')],
            [f'/group/{SLUG}/', reverse('group_posts', args=[SLUG])],
            [f'/{USERNAME}/', reverse('profile', args=[USERNAME])],
            [f'/{USERNAME}/{post.id}/', reverse('post', args=[
                USERNAME, post.id])],
            [f'/{USERNAME}/{post.id}/edit/', reverse('post_edit', args=[
                USERNAME, post.id])],
        ]
        for route, reverse_name in routes_reverse_names:
            self.assertEqual(route, reverse_name)
