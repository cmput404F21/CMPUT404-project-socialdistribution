# Generated by Django 3.2.9 on 2021-11-24 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_alter_post_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(default='', verbose_name='content'),
        ),
    ]
