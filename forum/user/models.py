from django.db import models


class User(models.Model):
    userid = models.AutoField(primary_key=True)
    is_admin = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    last_login_day = models.DateField(null=True)
    ban_time = models.IntegerField(default=0)
    username = models.CharField(max_length=100, default='')
    password = models.CharField(max_length=100, default='')
    photo = models.ImageField(upload_to='img', default='img/default_photo.png')
    user_experience = models.IntegerField(default=0)
    user_level = models.IntegerField(default=0)
    recent_posting_id = models.IntegerField(default=0)
    recent_reply_id = models.IntegerField(default=0)
