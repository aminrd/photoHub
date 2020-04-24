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
from django.urls import path, re_path

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('', views.home, name='home'),

    # User management:
    path('base/', views.base),
    path('notifications/', views.notifications, name='notifications'),

    path('profile/<int:user_id>/', views.profile),
    path('profile/<int:user_id>/portfolio/', views.portfolio),

    path('mytodo/', views.todo_list, name='todo'),
    path('myportfolio/', views.manage_portfolio, name='manage_portfolio'),
    path('requests/open/', views.requests),
    path('requests/new/', views.new_request, name='new_request'),
    path('myrequests/', views.my_requests, name='my_requests'),

    path('project/<int:project_id>/', views.project_view),
    path('project/<int:project_id>/applicants/', views.manage_applicants),

    path('editors/', views.editors, name='editors'),
    path('filemanager/', views.fileManager, name='filemanager'),

    path('signup/client/', views.client_signup, name='client_signup'),
    path('signup/editor/', views.designer_signup, name='designer_signup'),
    path('activate/', views.activate, name='activate'),

    path('balance/', views.balance, name='balance'),

    # Password reset management:
    re_path(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    re_path(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'WebApplication.views.handle404'
handler500 = 'WebApplication.views.handle500'
