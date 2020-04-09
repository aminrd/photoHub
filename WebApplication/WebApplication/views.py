# Login Managemement and urls:
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required

from .models import *
from django.utils import timezone
from django.contrib import auth
import itertools
import datetime,re

from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
import phonenumber_field.validators as phone_validator
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


def check_password_stregth(password):
    if len(password) < 8:
        return False

    if re.search(r"[A-Z]", password) is None:
        return False

    if re.search(r"[a-z]", password) is None:
        return False

    if re.search(r"[0-9]", password) is None:
        return False

    return True


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')

def login(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
        next = request.POST.get('NEXT', '')
        if user is not None:
            auth.login(request, user)
            if next == '':
                return redirect('home')
            else:
                return redirect(next)

        else:
            return render(request, 'login.html', {'error': 'Username or Password is incorrect!'})
    else:
        next = request.GET.get('next', '')
        return render(request, 'login.html', {'NEXT': next})


def client_signup(request):
    #TODO: complete sign up procedure for client and designer
    parg = pageArgs()

    if request.method == "GET":
        if request.user.is_anonymous:
            return render(request, 'signup_client.html')
        else:
            parg.EDIT_PROFILE = True
            ulist = list(Client.objects.filter(default_user=request.user))

            if len(ulist) > 0:
                if ulist[0].role != 'client':
                    return HttpResponseForbidden()
            else:
                return HttpResponseForbidden()

            parg.USER_INFO = ulist[0]
            parg.PROFILE_ACTIVE = True
            return render(request, 'signup_client.html', parg.__dict__)


def designer_signup(request):
    parg = pageArgs()

    if request.method == "GET":
        if request.user.is_anonymous:
            return render(request, 'signup_editor.html')
        else:
            parg.EDIT_PROFILE = True
            ulist = list(Designer.objects.filter(default_user=request.user))

            if len(ulist) > 0:
                if ulist[0].role != 'designer':
                    return HttpResponseForbidden()
            else:
                return HttpResponseForbidden()

            parg.USER_INFO = ulist[0]
            parg.PROFILE_ACTIVE = True
            return render(request, 'signup_editor.html', parg.__dict__)

    elif request.method == 'POST':
        parg.ERROR = []

        f_name = request.POST.get('first_name', None)
        if f_name is None or len(f_name) < 1:
            parg.ERROR.append('First name is not provided!')

        l_name = request.POST.get('last_name', None)
        if l_name is None or len(l_name) < 1:
            parg.ERROR.append('Last name is not provided!')

        password = request.POST.get('password', None)
        password_repeat = request.POST.get('password_repeat', None)

        rate = request.POST.get('rate', None)
        if rate is not None:
            try:
                rate = int(rate)
            except:
                rate = None

        if request.user.is_anonymous:
            email = request.POST.get('email', None)
            if email is None:
                parg.ERROR.append('Email address not provided!')
            elif User.objects.filter(email=email).count() > 0:
                parg.ERROR.append('Email address already exists')

            if password != password_repeat:
                parg.ERROR.append("Password repeat should be equal to password!")

            if len(password) > 0 and not check_password_stregth(password):
                parg.ERROR.append("Password is not strength enough! Should be at least 8 characters with a mix of uppercase, lowercase and numbers")

            phone_number = request.POST.get('phone', None)
            if phone_number is None:
                parg.ERROR.append('Phone number is not given!')

            try:
                phone_validator.validate_international_phonenumber(phone_number)
            except:
                parg.ERROR.append('Phone number is not valid!')
                #TODO: return the current form values in error cases
        else:
            email = request.user.email

        profile = None
        if request.FILES and request.FILES['profile']:
            profile = request.FILES['profile']

        homepage_url = request.POST.get('homepage_url', '')
        linkedin_url = request.POST.get('linkedin_url', '')
        instagram_url = request.POST.get('instagram_url', '')

        if len(parg.ERROR) > 0:
            return render(request, 'signup_editor.html', parg.__dict__)

        user_profile = None
        if request.user.is_anonymous:
            try:
                user = User.objects.create_user(email, email, password)
                user.save()
            except Exception as e:
                parg.ERROR.append(str(e))
                return render(request, 'signup_editor.html', parg.__dict__)

            auth.authenticate(username=user.username, password=password_repeat)

            user_profile = Designer()
            user_profile.role = 'designer'
            user_profile.default_user = user
        else:
            ulist = list(Designer.objects.filter(default_user=request.user))
            if len(ulist) > 0:
                if ulist[0].role == 'designer':
                    user_profile = Designer.objects.get(default_user=request.user)
                else:
                    return HttpResponseForbidden()
            else:
                return HttpResponseForbidden()

            phone_number = user_profile.phone_number

            if len(password_repeat) >= 8:
                user_profile.default_user.set_password(password_repeat)
                user_profile.default_user.save()

        user_profile.default_user.first_name = f_name
        user_profile.default_user.last_name = l_name
        user_profile.default_user.save()

        user_profile.phone_number = phone_number

        user_profile.linkedin_url = linkedin_url
        user_profile.instagram_url = instagram_url
        user_profile.homepage_link = homepage_url

        if rate is not None:
            user_profile.rate = rate

        if profile is not None:
            user_profile.profile_picture = profile
            user_profile.has_profile_picture = True

        user_profile.save()
        user_profile.create_thumbnail()
        user_profile.save()

        return redirect('home')

    else:
        return HttpResponseForbidden()


def home(request):
    parg = pageArgs()

    if not request.user.is_anonymous:
        ulist = list(Designer.objects.filter(default_user=request.user))
        if len(ulist) > 0:
            if ulist[0].role == 'designer':
                user_profile = Designer.objects.get(default_user=request.user)
            else:
                user_profile = Client.objects.get(default_user=request.user)
        else:
            user_profile = None
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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

    if request.method == 'GET':
        parg.PROJECT = project
        parg.REQUESTS_ACTIVE = True
        return render(request, 'Project.html', parg.__dict__)

    elif request.method == 'POST':
        form_type = request.POST.get('type', 'None')

        # Adding a new applicant to this project:
        if form_type == 'applicant_form':
            applicant_id = int(request.POST.get('applicant_id', -1))
            if applicant_id >= 0 and applicant_id == request.user.id:
                designer = get_object_or_404(Designer, pk=request.user.id)
                project.add_applicant(designer)
                return render(request, 'Project.html', parg.__dict__)
            else:
                return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
def activate(request):
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

    return render(request, 'activation.html', parg.__dict__)


@login_required(login_url='/login/')
def balance(request):
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
    parg.BALANCE_ACTIVE = True

    return render(request, 'balance.html', parg.__dict__)


def handle404(request, exception):
    return render(request, '400.html', {})


def handle500(request):
    return render(request, '500.html', {})
