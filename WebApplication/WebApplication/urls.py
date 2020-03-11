# Licence: photoHub
# Written by Amin Aghaee
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404, handler500

from django.conf import settings
from django.conf.urls.static import static

from . import views

admin.site.site_header = 'PhotoHub Admin Panel'
admin.site.index_title = 'Database management'
admin.site.site_title = 'PhotoHub Admin'

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),

    # User management:
    path('admin/', admin.site.urls),

    # Project management:
]
