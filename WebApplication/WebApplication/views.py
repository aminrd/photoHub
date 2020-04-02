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
from django.core.paginator import Paginator,  EmptyPage, PageNotAnInteger

from django.http import HttpResponse, HttpResponseForbidden
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
        self.ABOUTUS_ACTIVE = False



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
    parg.MAIN_TITLE = 'List of public edits'

    plist = list(Project.objects.all().filter(allowed_to_share=True).order_by('date_created'))

    page = request.GET.get('page', 1)
    paginator = Paginator(plist, 12)
    try:
        plist_paged = paginator.page(page)
    except PageNotAnInteger:
        plist_paged = paginator.page(1)
    except EmptyPage:
        plist_paged = paginator.page(paginator.num_pages)

    iterable = [iter(plist_paged)] * 3
    parg.PLIST_ROWS = itertools.zip_longest(*iterable, fillvalue=None)
    parg.PAGINATE = plist_paged

    return render(request, 'home.html', parg.__dict__)

def todo_list(request):
    parg = pageArgs()

    ulist = list(Designer.objects.filter(default_user=request.user))
    if len(ulist) > 0:
        if ulist[0].role == 'designer':
            user_profile = Designer.objects.get(default_user=request.user)
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()

    parg.USER_INFO = user_profile
    parg.REQUESTS_ACTIVE = True

    plist = Project.objects.all().filter(server=user_profile).filter(status='progress').order_by('target_deadline')
    plist = list( x for x in plist if x.days_remaining() >= 0 )
    parg.PLIST = plist

    return render(request, 'todo.html', parg.__dict__)


def manage_portfolio(request):
    parg = pageArgs()

    ulist = list(Designer.objects.filter(default_user=request.user))
    if len(ulist) > 0:
        if ulist[0].role == 'designer':
            user_profile = Designer.objects.get(default_user=request.user)
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()

    parg.USER_INFO = user_profile
    parg.PROFILE_ACTIVE = True

    plist = Project.objects.all().filter(server=user_profile).filter(status='progress').order_by('target_deadline')
    parg.PLIST = plist

    return render(request, 'managePortfolio.html', parg.__dict__)

def requests(request):
    if request.method == 'GET':
        parg = pageArgs()
        parg.REQUESTS_ACTIVE = True

        # Open Requests -- showing all requests to designers only
        ulist = list(Designer.objects.filter(default_user=request.user))
        if len(ulist) > 0:
            if ulist[0].role == 'designer':
                user_profile = Designer.objects.get(default_user=request.user)
            else:
                return HttpResponseForbidden()
        else:
            return HttpResponseForbidden()

        parg.USER_INFO = user_profile

        plist = Project.objects.all().filter(status='open').order_by('target_deadline')
        plist = list(x for x in plist if x.days_remaining() >= 0)
        print(plist)

        page = request.GET.get('page', 1)
        paginator = Paginator(plist, 12)
        try:
            plist_paged = paginator.page(page)
        except PageNotAnInteger:
            plist_paged = paginator.page(1)
        except EmptyPage:
            plist_paged = paginator.page(paginator.num_pages)

        iterable = [iter(plist_paged)] * 3
        parg.PLIST_ROWS = itertools.zip_longest(*iterable, fillvalue=None)
        parg.PAGINATE = plist_paged

        return render(request, 'Requests.html', parg.__dict__)

def portfolio(request, user_id):
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

    plist = user_profile.get_portfolio()

    page = request.GET.get('page', 1)
    paginator = Paginator(plist, 12)
    try:
        plist_paged = paginator.page(page)
    except PageNotAnInteger:
        plist_paged = paginator.page(1)
    except EmptyPage:
        plist_paged = paginator.page(paginator.num_pages)

    iterable = [iter(plist_paged)] * 3
    parg.PLIST_ROWS = itertools.zip_longest(*iterable, fillvalue=None)
    parg.PAGINATE = plist_paged

    if user_profile.role == 'designer':
        parg.MAIN_TITLE = f'Portfolio of {user_profile.default_user.first_name}'
    else:
        parg.MAIN_TITLE = f'Look at all edits {user_profile.default_user.first_name} got from our app'

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
    parg.TODAY = datetime.datetime.now()

    return render(request, 'profile.html', parg.__dict__)


def project_view(request, project_id):
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

    project = get_object_or_404(Project, pk=project_id)
    if not project.is_visible(user_profile):
        return HttpResponseForbidden()

    parg.PROJECT = project
    parg.REQUESTS_ACTIVE = True
    return render(request, 'Project.html', parg.__dict__)


def fileManager(request):
    if request.method == 'POST':
        m_name = request.POST.get('MODEL_NAME', 'None')

        try:
            m_id = int(request.POST.get('MODEL_ID', -1))
        except:
            m_id -1

        m_field = request.POST.get('FIELD_NAME', 'None')

        if m_name.lower() == 'project':
            project = get_object_or_404(Project, pk=m_id)
            if m_field.lower() == 'input_file':
                project.input_file = request.FILES.get('file')
                project.save()

            elif m_field.lower() == 'output_file':
                project.output_image = request.FILES.get('file')
                project.save()

        elif m_name.lower == 'client':
            client = get_object_or_404(Client, pk=m_id)
            if m_field.lower() == 'profile_picture':
                client.profile_picture = request.FILES.get('file')
                client.save()

        elif m_name.lower == 'designer':
            designer = get_object_or_404(Designer, pk=m_id)
            if m_field.lower() == 'profile_picture':
                designer.profile_picture = request.FILES.get('file')
                designer.save()

        else:
            return HttpResponseForbidden()

    elif request.method == 'GET':
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

        # File upload arguments:
        parg.MODEL_NAME = request.GET.get('MODEL_NAME', 'None')
        parg.FIELD_NAME = request.GET.get('FIELD_NAME', 'None')
        parg.MODEL_ID = request.GET.get('MODEL_ID', 0)

        return render(request, 'upload_one.html', parg.__dict__)

    else:
        return HttpResponseForbidden()


def base(request):
    parg = pageArgs()
    return render(request, 'upload_one.html', parg.__dict__)


def editors(request):
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

    parg.EDITORS_ACTIVE = True
    parg.MAIN_TITLE = 'List of public edits'

    editors = list(Designer.objects.all())
    editors = sorted(editors, key=lambda x: x.default_user.date_joined, reverse=True)

    page = request.GET.get('page', 1)
    paginator = Paginator(editors, 12)
    try:
        plist_paged = paginator.page(page)
    except PageNotAnInteger:
        plist_paged = paginator.page(1)
    except EmptyPage:
        plist_paged = paginator.page(paginator.num_pages)

    parg.PAGINATE = plist_paged

    return render(request, 'editors.html', parg.__dict__)


