import logging
from celery import shared_task
from django.db.models import F

from .models import User
logger = logging.getLogger()


@shared_task
def schedule_minus():
    User.objects.filter(is_banned=True).update(ban_time=F('ban_time')-1)
    User.objects.filter(ban_time=0).update(is_banned=False)
