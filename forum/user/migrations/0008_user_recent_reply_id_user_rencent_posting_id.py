# Generated by Django 4.0.3 on 2022-06-07 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_alter_user_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='recent_reply_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='rencent_posting_id',
            field=models.IntegerField(default=0),
        ),
    ]
