# Login Managemement and urls:
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required

from .models import *
from django.utils import timezone
from django.contrib import auth

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
    parg.USER_INFO = UserInfo.objects.get(default_user=request.user)
    parg.SHOWCASE_ACTIVE = True

    plist = Project.objects.all()
    parg.PLIST = plist

    return render(request, 'home.html', parg.__dict__)

def base(request):
    parg = pageArgs()
    return render(request, 'home.html', parg.__dict__)
