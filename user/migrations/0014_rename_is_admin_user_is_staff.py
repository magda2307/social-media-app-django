# Generated by Django 4.2.1 on 2023-06-13 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_alter_tag_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='is_admin',
            new_name='is_staff',
        ),
    ]
