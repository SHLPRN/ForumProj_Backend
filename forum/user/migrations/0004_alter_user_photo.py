# Generated by Django 4.0.4 on 2022-05-28 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_user_is_admin_user_photo_delete_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.FileField(null=True, upload_to='img/'),
        ),
    ]
