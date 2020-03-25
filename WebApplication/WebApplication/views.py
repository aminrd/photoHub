# Login Managemement and urls:
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required

from .models import *
from django.utils import timezone
from django.contrib import auth
import itertools
import datetime


from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from django.core.paginator import Paginator

from django.http import HttpResponse
from django.template import Context
class pageArgs:
    def __init__(self):
        self.USER_INFO = None

        # Side bar activation:
        self.SHOWCASE_ACTIVE = False
        self.REQUEST_ACTIVE = False
        self.PROFILE_ACTIVE = False
        self.EDITORS_ACTIVE = False
        self.BALANCE_ACTIVE = False
        self.ABOUTus_ACTIVE = False



def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')

def login(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            return redirect('home')

        else:
            return render(request, 'login.html', {'error': 'Username or Password is incorrect!'})
    else:
        return render(request, 'login.html')

def home(request):
    parg = pageArgs()

    ulist = list(Designer.objects.filter(default_user=request.user))
    if len(ulist) > 0:
        if ulist[0].role == 'designer':
            user_profile = Designer.objects.get(default_user=request.user)
        else:
            user_profile = Client.objects.get(default_user=request.user)
    else:
        user_profile = None
    parg.USER_INFO = user_profile

    parg.SHOWCASE_ACTIVE = True
    parg.MAIN_TITLE = 'List of finished designs'

    plist = list(Project.objects.all())
    plist = [plist[0] for x in range(10)]

    iterable = [iter(plist)] * 3
    parg.PLIST_ROWS = itertools.zip_longest(*iterable, fillvalue=None)

    return render(request, 'home.html', parg.__dict__)

def profile(request, user_id):
    parg = pageArgs()

    ulist = list(Designer.objects.filter(default_user=request.user))
    if len(ulist) > 0:
        if ulist[0].role == 'designer':
            user_profile = Designer.objects.get(default_user=request.user)
        else:
            user_profile = Client.objects.get(default_user=request.user)
    else:
        user_profile = None
    parg.USER_INFO = user_profile
    parg.PROFILE_ACTIVE = True

    user_profile = get_object_or_404(UserInfo, pk=user_id)
    if user_profile.role == 'designer':
        user_profile = get_object_or_404(Designer, pk=user_id)
    else:
        user_profile = get_object_or_404(Client, pk=user_id)
    parg.PROFILE = user_profile
    parg.TODAY = datetime.datetime.utcnow()

    return render(request, 'profile.html', parg.__dict__)

def base(request):
    parg = pageArgs()
    return render(request, 'home.html', parg.__dict__)
