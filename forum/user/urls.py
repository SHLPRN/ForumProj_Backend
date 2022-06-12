from django.urls import path
from .views import *

urlpatterns = [
    # http://127.0.0.1/user/login
    path('login', login),
    # http://127.0.0.1/user/register
    path('register', register),
    # http://127.0.0.1/user/modify_user
    path('modify_username', modify_username),
    path('modify_photo', modify_photo),
    # http://127.0.0.1/user/ban_user
    path('ban_user', ban_user),
    # http://127.0.0.1/user/release_ban
    path('release_ban', release_ban),
    # http://127.0.0.1/user/delete_posting
    path('delete_posting', delete_posting),
    # http://127.0.0.1/user/create_admin
    path('create_admin', create_admin),
    path('modify_password', modify_password),
    path('manage', manage),
    path('space', space),
    path('other_space', other_space),
    path('delete_reply', delete_reply)
]
