from django.db import models
from user.models import User


# 板块类
class Sector(models.Model):
    sector_name = models.CharField(primary_key=True, max_length=60, unique=True)
    sector_introduction = models.TextField(default='暂无简介', null=True, blank=True)


# 帖子类
class Posting(models.Model):
    posting_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.SET_NULL)
    sector_name = models.ForeignKey(to=Sector, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=252)
    content = models.TextField()
    time = models.CharField(max_length=252)
    like_count = models.IntegerField(default=0)
    like = models.ManyToManyField(to=User, blank=True, related_name='like_posting')
    click_count = models.IntegerField(default=0)
    recent_comment_time = models.CharField(max_length=252, null=True)
    recent_comment_id = models.IntegerField(default=-1)
    authority = models.CharField(max_length=60)


# 回复类
class Reply(models.Model):
    reply_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    # judge用于判断是哪种回复 1-帖子中的楼 2-对某楼层的回复 3-对2的回复
    judge = models.IntegerField()
    posting_id = models.ForeignKey(Posting, null=True, blank=True, on_delete=models.CASCADE)
    reply1_id = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='reply_to1')
    reply2_id = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='reply_to2')
    content = models.TextField()
    time = models.CharField(max_length=252)
    like_count = models.IntegerField(default=0)
    like = models.ManyToManyField(to=User, blank=True, related_name='like_reply')


class File(models.Model):
    file_id = models.AutoField(primary_key=True)
    posting_id = models.ForeignKey(Posting, on_delete=models.CASCADE, null=True, blank=True)
    filename = models.TextField()
