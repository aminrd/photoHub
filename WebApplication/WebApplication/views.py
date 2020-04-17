# Login Managemement and urls:
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required

from .models import *
from django.utils import timezone
from django.contrib import auth
import itertools
import datetime, re, json
from PIL import Image

from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
import phonenumber_field.validators as phone_validator
from django.core.paginator import Paginator,  EmptyPage, PageNotAnInteger

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
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
        next = request.POST.get('NEXT', '/')
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
            if phone_number is not None:
                try:
                    phone_validator.validate_international_phonenumber(phone_number)
                except:
                    parg.ERROR.append('Phone number is not valid!')
        else:
            email = request.user.email

        profile = None
        if request.FILES and request.FILES['profile']:
            profile = request.FILES['profile']


        if len(parg.ERROR) > 0:
            return render(request, 'signup_client.html', parg.__dict__)

        user_profile = None
        if request.user.is_anonymous:
            try:
                user = User.objects.create_user(email, email, password)
                user.save()
            except Exception as e:
                parg.ERROR.append(str(e))
                return render(request, 'signup_client.html', parg.__dict__)

            auth.authenticate(username=user.username, password=password_repeat)

            user_profile = Client()
            user_profile.role = 'client'
            user_profile.default_user = user
        else:
            ulist = list(Client.objects.filter(default_user=request.user))
            if len(ulist) > 0:
                if ulist[0].role == 'client':
                    user_profile = Client.objects.get(default_user=request.user)
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

        if profile is not None:
            user_profile.profile_picture = profile
            user_profile.has_profile_picture = True

        user_profile.save()
        user_profile.create_thumbnail()
        user_profile.save()

        return redirect('login')

    else:
        return HttpResponseForbidden()


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

        return redirect('login')

    else:
        return HttpResponseForbidden()


def home(request):
    parg = pageArgs()

    if not request.user.is_anonymous:
        ulist = list(UserInfo.objects.filter(default_user=request.user))
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

    if request.method == 'GET':
        parg.USER_INFO = user_profile
        parg.PROFILE_ACTIVE = True

        plist = Project.objects.all().filter(server=user_profile).order_by('-target_deadline')
        parg.PLIST = plist

        return render(request, 'managePortfolio.html', parg.__dict__)
    else:
        # type: 'change_portfolio',
        # project_id: project_id,
        # allow_status: action,

        msg_type = request.POST.get('type', None)
        pid = request.POST.get('project_id', None)
        try:
            pid = int(pid)
        except:
            return HttpResponseForbidden()

        if msg_type == 'change_portfolio':
            allow_status = request.POST.get('allow_status', 'no')
            allow_status = allow_status.lower()

            project = get_object_or_404(Project, pk=pid)

            if allow_status == 'yes':
                project.report_on_portfolio = True
            else:
                project.report_on_portfolio = False
            project.save()
            return HttpResponse("OK")

        else:
            return HttpResponseForbidden()


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
def new_request(request):
    parg = pageArgs()
    parg.REQUESTS_ACTIVE = True

    # Open Requests -- showing all requests to designers only
    ulist = list(Client.objects.filter(default_user=request.user))
    if len(ulist) > 0:
        if ulist[0].role == 'client':
            user_profile = Client.objects.get(default_user=request.user)
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()

    if request.method == 'GET':
        parg.USER_INFO = user_profile

        if not user_profile.activated:
            parg.ERROR = ['Please confirm your email address to make your requests visible to editors']

        return render(request, 'new_request.html', parg.__dict__)

    elif request.method == "POST":
        main_input = None
        if request.FILES and request.FILES.get('main_input', None):
            main_input = request.FILES.get('main_input', None)

        description = request.POST.get('description', "")
        deadline_txt = request.POST.get('deadline', None)

        parg.ERROR = []
        if main_input is None:
            parg.ERROR.append('Please upload your photo!')

        dt = None
        if deadline_txt is not None:
            try:
                dt = datetime.datetime.strptime(deadline_txt[:10] + " 23:59", '%m-%d-%Y %H:%M')
            except:
                dt = None

        if dt is None:
            parg.ERROR.append('Please specify the deadline!')

        elif (dt - datetime.datetime.now()).days < 1:
            parg.ERROR.append('Deadline should be at least 24 hours from now!')

        if len(parg.ERROR) > 0:
            return render(request, 'new_request.html', parg.__dict__)

        project = Project()
        project.description = description
        project.target_deadline = dt
        project.client = user_profile

        #TODO: convert main input to JPG image
        project.input_file = main_input
        project.save()


        image = Image.open(project.input_file.file)
        image_file = BytesIO()
        image.save(image_file, 'JPEG')

        main_name = os.path.basename(project.input_file.name)
        main_name = os.path.splitext(main_name)[0]

        project.input_image.save(
            main_name + ".jpg",
            InMemoryUploadedFile(
                image_file,
                None, '',
                'image/jpeg',
                image.size,
                None,
            ),
            save=True
        )
        project.save()

        project.create_thumbnail()
        project.save()

        return redirect('..')

    else:
        return HttpResponseForbidden()


@login_required(login_url='/login/')
def my_requests(request):
    parg = pageArgs()

    user_profile = None
    if not request.user.is_anonymous:
        ulist = list(UserInfo.objects.filter(default_user=request.user))
        if len(ulist) > 0:
            if ulist[0].role == 'client':
                user_profile = Client.objects.get(default_user=request.user)
            else:
                return HttpResponseForbidden()
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()

    parg.USER_INFO = user_profile

    parg.REQUESTS_ACTIVE = True
    parg.MAIN_TITLE = 'List of my current and past edits'

    plist = list(Project.objects.all().filter(client=user_profile).order_by('date_created'))

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
def portfolio(request, user_id):
    parg = pageArgs()

    ulist = list(UserInfo.objects.filter(default_user=request.user))
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

    ulist = list(UserInfo.objects.filter(default_user=request.user))
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
    #TODO: upload file by designer
    #TODO: download page by sending a query to download fiels

    parg = pageArgs()

    ulist = list(UserInfo.objects.filter(default_user=request.user))
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
                return HttpResponseRedirect("")
            else:
                return HttpResponseForbidden()

        elif form_type == 'client_rating':
            rating = request.POST.get('rating_value', "0")

            try:
                rating = int(rating)
            except:
                rating = -1

            if request.user == project.client.default_user and 1<= rating <= 5:
                project.owner_feedback = rating
                project.save()
                return HttpResponse("OK")
            else:
                return HttpResponseForbidden()

        elif form_type == 'allow_status':
            allow_status = request.POST.get('allow_status', 'no')
            if allow_status == 'yes':
                allow_status = True
            else:
                allow_status = False

            if request.user == project.client.default_user and project.price_spend > 0:
                project.allowed_to_share = allow_status
                project.save()
                return HttpResponse("OK")
            else:
                return HttpResponseForbidden()


        return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()

@login_required(login_url='/login/')
def manage_applicants(request, project_id):
    parg = pageArgs()

    ulist = list(Client.objects.filter(default_user=request.user))
    if len(ulist) > 0:
        if ulist[0].role == 'client':
            user_profile = Client.objects.get(default_user=request.user)
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()

    parg.USER_INFO = user_profile

    project = get_object_or_404(Project, pk=project_id)
    if project.client.default_user != request.user or not project.status == 'open':
        return HttpResponseForbidden()

    parg.PROJECT = project
    parg.REQUESTS_ACTIVE = True

    if request.method == 'GET':
        return render(request, 'applicants.html', parg.__dict__)

    elif request.method == 'POST':
        applicant_id = request.POST.get('applicant_id', '0')
        try:
            applicant_id = int(applicant_id)
        except:
            applicant_id = -1
        designer = get_object_or_404(Designer, pk=applicant_id)

        code, status = project.approve_designer(designer)
        if code == 0:
            #TODO: Test approving an applicant redirection susccessfluy
            return redirect(reverse(f'/project/{project.id}/'))
        else:
            parg.ERROR = [status]
            return render(request, 'applicants.html', parg.__dict__)

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
                return HttpResponseForbidden()
                # project.input_file = request.FILES.get('file')
                # project.save()

            elif m_field.lower() == 'output_file':
                if project.server is not None and request.user.id == project.server.default_user.id:

                    if project.days_remaining() < 0:
                        return HttpResponseForbidden()

                    project.output_image = request.FILES.get('file')
                    project.status = 'finished'
                    project.time_finished = datetime.datetime.now()
                    project.save()

                    # Notify client:
                    notif = Notification()
                    notif.related_user = project.client
                    notif.content = f"""
                        Good news! {project.server.full_name()} finished editing your photo. Look at the edit. 
                        Don't forget to rate this edit and give us your feedback.
                    """
                    notif.link = f'/project/{project.id}/'
                    notif.save()

                    # Give money to designer
                    project.server.charge( (4 * project.price_spend) // 5 )
                    project.server.save()

                    return HttpResponseRedirect(f'/project/{project.id}/')

                else:
                    return HttpResponseForbidden()

        elif m_name.lower == 'client':
            return HttpResponseForbidden()
            # client = get_object_or_404(Client, pk=m_id)
            # if m_field.lower() == 'profile_picture':
            #     client.profile_picture = request.FILES.get('file')
            #     client.save()

        elif m_name.lower == 'designer':
            return HttpResponseForbidden()
            # designer = get_object_or_404(Designer, pk=m_id)
            # if m_field.lower() == 'profile_picture':
            #     designer.profile_picture = request.FILES.get('file')
            #     designer.save()

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

    ulist = list(UserInfo.objects.filter(default_user=request.user))
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

    ulist = list(UserInfo.objects.filter(default_user=request.user))
    if len(ulist) > 0:
        if ulist[0].role == 'designer':
            user_profile = Designer.objects.get(default_user=request.user)
        else:
            user_profile = Client.objects.get(default_user=request.user)
    else:
        user_profile = None

    if user_profile is None:
        return HttpResponseForbidden()

    parg.USER_INFO = user_profile
    parg.PROFILE_ACTIVE = True

    if request.method == 'GET':
        return render(request, 'activation.html', parg.__dict__)
    else:
        form_type = request.POST.get('form_type', None)

        if form_type == 'resend':
            activate_email = request.POST.get('resend_activation_email', None)
            activate_phone = request.POST.get('resend_verification_code', None)

            if activate_email == '1':
                if user_profile.activated:
                    return HttpResponseForbidden()

                if Activation.objects.all().filter(email_address=user_profile.default_user.email).exists():
                    activation = Activation.objects.get(email_address=user_profile.default_user.email)
                else:
                    activation = Activation()
                    activation.email_address = user_profile.default_user.email
                    activation.save()

                #TODO: email user activation.code
                return render(request, 'activation.html', parg.__dict__)

            elif activate_phone == '1':
                if user_profile.verified:
                    return HttpResponseForbidden()

                if Activation.objects.all().filter(phone_number=user_profile.phone_number).exists():
                    activation = Activation.objects.get(phone_number=user_profile.phone_number)
                else:
                    activation = Activation()
                    activation.phone_number = user_profile.phone_number
                    activation.save()

                #TODO: SMS user verification code
                return render(request, 'activation.html', parg.__dict__)
            else:
                return HttpResponseForbidden()

        elif form_type == 'activation':
            email_code = request.POST.get('email_verification_code', None)
            phone_code = request.POST.get('phone_verification_code', None)

            if email_code is not None and not user_profile.activated:
                if Activation.objects.all().filter(email_address=user_profile.default_user.email).exists():
                    activation = Activation.objects.get(email_address=user_profile.default_user.email)
                    result = activation.try_code(email_code)
                    if result:
                        activation.delete()
                        user_profile.activated = True
                        user_profile.save()
                        return redirect('home')

                    else:
                        if activation.max_tried <= 0:
                            activation.delete()

                        parg.ERROR = ['Verification code is wrong! Try again. If you have not received the code, click on resend button']
                        return render(request, 'activation.html', parg.__dict__)
                else:
                    parg.ERROR = ['Activation code is expired! Click on resend button']
                    return render(request, 'activation.html', parg.__dict__)

            elif phone_code is not None and not user_profile.verified:
                if Activation.objects.all().filter(phone_number=user_profile.phone_number).exists():
                    activation = Activation.objects.get(phone_number=user_profile.phone_number)
                    result = activation.try_code(phone_code)
                    if result:
                        activation.delete()
                        user_profile.verified = True
                        user_profile.save()
                        return redirect('home')
                    else:
                        if activation.max_tried <= 0:
                            activation.delete()

                        parg.ERROR = ['Verification code is wrong! Try again. If you have not received the code, click on resend button']

                        return render(request, 'activation.html', parg.__dict__)
                else:
                    parg.ERROR = ['Activation code is expired! Click on resend button']
                    return render(request, 'activation.html', parg.__dict__)

            elif phone_code is not None and not user_profile.verified:
                pass
            else:
                return HttpResponseForbidden()

        else:
            return HttpResponseForbidden()



@login_required(login_url='/login/')
def balance(request):
    parg = pageArgs()

    ulist = list(UserInfo.objects.filter(default_user=request.user))
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

@login_required(login_url='/login/')
def notifications(request):
    parg = pageArgs()

    ulist = list(UserInfo.objects.filter(default_user=request.user))
    if len(ulist) > 0:
        if ulist[0].role == 'designer':
            user_profile = Designer.objects.get(default_user=request.user)
        else:
            user_profile = Client.objects.get(default_user=request.user)
    else:
        return HttpResponseForbidden()

    if request.method == "GET":
        parg.USER_INFO = user_profile

        page = request.GET.get('page', 1)
        paginator = Paginator(user_profile.get_notifications(), 50)
        try:
            notif_paged = paginator.page(page)
        except PageNotAnInteger:
            notif_paged = paginator.page(1)
        except EmptyPage:
            notif_paged = paginator.page(paginator.num_pages)

        parg.NOTIF_PAGINATOR = notif_paged

        return render(request, 'notifications.html', parg.__dict__)
    else:
        command = request.POST.get('command', None)
        if command == 'mark-as-read':
            items = request.POST.get('items', '[]')
            items = json.loads(items)

            for notif in items:
                try:
                    notif_id = int(notif)
                    notif_obj = Notification.objects.get(pk=notif_id)

                    if notif_obj.related_user.default_user.id == request.user.id:
                        notif_obj.mark_as_read()

                except Exception as e:
                    pass

        return HttpResponse('OK')



def handle404(request, exception):
    return render(request, '400.html', {})


def handle500(request):
    return render(request, '500.html', {})
