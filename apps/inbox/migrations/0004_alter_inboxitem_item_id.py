# Generated by Django 3.2.9 on 2021-12-06 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inbox', '0003_auto_20211126_1116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inboxitem',
            name='item_id',
            field=models.CharField(max_length=500),
        ),
    ]
