# Generated by Django 2.2.9 on 2021-03-01 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20210301_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(verbose_name='Ваш текст'),
        ),
    ]