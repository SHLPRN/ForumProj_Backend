from django.urls import path
from .views import *

urlpatterns = {
    path('publish', publish, name='publish'),
    path('uploadFile', uploadFile, name='uploadFile'),
    path('comment', comment, name='comment'),
    path('like', like, name='like'),
    path('searchPosting', searchPosting, name='searchPosting'),
    path('deletePosting', deletePosting, name='deletePosting'),
    path('deleteComment', deleteComment, name='deleteComment'),
    path('getHomepagePostingList', getHomepagePostingList, name='getHomepagePostingList'),
    path('getSectorPostingList', getSectorPostingList, name='getSectorPostingList'),
    path('getUserPostingList', getUserPostingList, name='getUserPostingList'),
    path('getPostingInfo', getPostingInfo, name='getPostingInfo'),
    path('downloadFile', downloadFile, name='downloadFile')
}
