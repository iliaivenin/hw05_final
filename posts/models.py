from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name="название сообщества",
        max_length=200,
        help_text="введите уникальное название сообщества",
    )
    slug = models.SlugField(
        verbose_name="ключ",
        unique=True,
        help_text="ключ",
    )
    description = models.TextField(
        verbose_name="описание",
        help_text="описание сообщества",)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "сообщество"
        verbose_name_plural = "сообщества"


class Post(models.Model):
    text = models.TextField(
        verbose_name="ваш текст",
        help_text="введите текст записи",)
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name="автор",
        on_delete=models.CASCADE,
        related_name="posts",
        help_text="выберите автора из выпадающего списка",
    )
    group = models.ForeignKey(
        Group,
        verbose_name="сообщество",
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
        help_text="можно выбрать сообщество",
    )
    image = models.ImageField(
        upload_to='posts/',
        verbose_name="изображение",
        blank=True,
        null=True,
    )

    def __str__(self):
        OUTPUT = ('Текст: {text} | автор: {author} | сообщество: {group} | '
                  'дата публикации: {pub_date:%d.%m.%Y %H:%M}')
        return OUTPUT.format(text=self.text[:15], author=self.author.username,
                             group=self.group, pub_date=self.pub_date)

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "запись"
        verbose_name_plural = "записи"


class Comment(models.Model):
    text = models.TextField(
        verbose_name="текст комментария",
        help_text="введите текст комментария",)
    created = models.DateTimeField(
        verbose_name="дата и время комментария",
        auto_now_add=True,
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name="пост",
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="пользователь",
        related_name="comments",
    )

    class Meta:
        ordering = ["created"]
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"

    def __str__(self):
        return (f'Текст комментария: {self.text[:20]} | '
                f'автор: {self.author}')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="пользователь",
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="автор",
        related_name="following",
    )
