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
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('', views.home, name='home'),

    # User management:
    path('base/', views.base),
    path('profile/<int:user_id>/', views.profile),
    path('profile/<int:user_id>/portfolio/', views.portfolio),

    path('mytodo/', views.todo_list, name='todo'),
    path('myportfolio/', views.manage_portfolio, name='manage_portfolio'),
    path('requests/open/', views.requests),

    path('project/<int:project_id>/', views.project_view),

    path('editors/', views.editors, name='editors'),
    path('filemanager/', views.fileManager, name='filemanager'),

    # Project management:
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)