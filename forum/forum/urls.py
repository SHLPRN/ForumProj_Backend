from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/posting/', include(('posting.urls', 'posting'))),
    path('api/user/', include(('user.urls', 'user')))
]
