# Generated by Django 4.2.1 on 2023-06-13 13:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_alter_tag_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='date_created',
        ),
    ]
