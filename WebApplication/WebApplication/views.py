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

def base(request):
    return render(request, 'base.html')
