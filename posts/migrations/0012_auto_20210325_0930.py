# Generated by Django 2.2.6 on 2021-03-25 06:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20210325_0928'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'сообщество', 'verbose_name_plural': 'сообщества'},
        ),
    ]