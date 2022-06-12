from django.db.models.signals import post_migrate
from user.models import User


def init_db(sender, **kwargs):
    if sender.name == 'User.__name__':
        if not User.objects.exists():
            User.objects.create(username='ROOT', password='forum', is_admin=True)


post_migrate.connect(init_db)
