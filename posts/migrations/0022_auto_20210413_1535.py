# Generated by Django 2.2.6 on 2021-04-13 12:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0021_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'подписка', 'verbose_name_plural': 'подписки'},
        ),
    ]