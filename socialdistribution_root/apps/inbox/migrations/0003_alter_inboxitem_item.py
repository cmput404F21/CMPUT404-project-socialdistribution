# Generated by Django 3.2.8 on 2021-10-27 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inbox', '0002_rename_type_inboxitem_item_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inboxitem',
            name='item',
            field=models.CharField(max_length=5000),
        ),
    ]
