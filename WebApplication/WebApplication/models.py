# Licence: photoHub
# Written by Amin Aghaee
import uuid
from django.db import models
from django.contrib.auth.models import User
import WebApplication.settings as app_setting
from django.templatetags.static import  static

# Third-party libraries
from phonenumber_field.modelfields import PhoneNumberField

# Image and Thumbnail related libraries
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import os


# ==================================================
# Define User, Client and Designer tables
# ==================================================
# Django default user fields: username, first_name, last_name, email, password, date_joined
class UserInfo(models.Model):
    default_user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_number = PhoneNumberField()
    verified = models.BooleanField(default=False)
    credit = models.IntegerField(default=0)

    has_profile_picture = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_images/main/')
    profile_thumbnail = models.ImageField(upload_to='profile_images/thumbnail/')

    def create_thumbnail(self):
        image = Image.open(self.profile_picture.file)
        image.thumbnail(size=(100, 100))
        image_file = BytesIO()
        image.save(image_file, image.format)

        self.profile_thumbnail.save(
            self.profile_picture.name + "_thumbnail",
            InMemoryUploadedFile(
                image_file,
                None, '',
                self.profile_picture.file.content_type,
                image.size,
                self.profile_picture.file.charset,
            ),
            save=True
        )
        return True

    def charge(self, amount):
        amount = int(amount)
        self.credit = self.credit + amount
        self.save()

    def get_profile(self):
        return static('img/UserProfileDefault.png')

class Client(UserInfo):
    # List of projects: client_project <list>
    pass

    def get_profile(self):
        if self.profile_picture is None:
            return static('img/UserProfileDefault.png')
        else:
            return self.profile_picture.url


class Designer(UserInfo):
    score = models.IntegerField(default=0)
    avg_feedback = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    rate = models.IntegerField(default=100)

    # Public profile visible to all people
    user_plus = models.BooleanField(default=False)
    user_plus_expires = models.DateTimeField(auto_now_add=True)

    # User links for user_plus only:
    homepage_link = models.CharField(max_length=1024, blank=True, null=True, default=None)
    instagram_url = models.CharField(max_length=1024, blank=True, null=True, default=None)
    linkedin_url = models.CharField(max_length=1024, blank=True, null=True, default=None)

    def update_avg_feedback(self):
        plist = list(self.project_server.all())
        if len(plist) < 1:
            self.avg_feedback = 0.0
        else:
            self.avg_feedback = sum(plist) / len(plist)
        self.save()

    # From 1 to 5
    def get_level(self):
        lvl = [100, 250, 500, 1000, 2000]
        level = 0
        for i in range(len(lvl)):
            if self.score >= lvl[i]:
                level += 1
        return level

    def get_rate(self):
        lvl = self.get_level()

        if self.user_plus or lvl >= 5:
            return self.rate

        rate_list = [0, 10, 20, 50, 100]
        return rate_list[lvl-1]

    def get_profile(self):
        if self.profile_picture is None:
            return static('img/UserProfileDefault.png')
        else:
            return self.profile_picture.url

    def get_profile_thumbnail(self):
        if self.profile_picture is None:
            return static('img/UserProfileDefault.png')
        else:
            return self.profile_thumbnail.url

# ==================================================
# Define User, Client and Designer tables
# ==================================================
class Project(models.Model):

    PROJECT_STATUS = [
        ("open", 'Open'),
        ("progress", 'Already Assigned'),
        ("finished", 'Finished'),
    ]

    date_created = models.DateTimeField(auto_now_add=True)
    target_deadline = models.DateTimeField(default=None)
    time_finished = models.DateTimeField(default=None)
    status = models.CharField(max_length=16, choices=PROJECT_STATUS, default="open")

    # Users related
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name='project_client')
    server = models.ForeignKey(Designer, on_delete=models.SET_NULL, null=True, related_name='project_server', default=None)
    applicants = models.ManyToManyField(Designer)

    allowed_to_share = models.BooleanField(default=False, blank=True, null=True)
    report_on_portfolio = models.BooleanField(default=True)
    description = models.TextField(max_length=2048, default="")

    # Could be None, 1,2,3,4,5
    owner_feedback = models.IntegerField(default=None)
    owner_feedback_text = models.TextField(max_length=512, blank=True, null=True, default='')
    price_spend = models.IntegerField(default=1)

    input_file = models.FileField(upload_to='images/inputs/original_file', default=None)
    input_image = models.ImageField(upload_to='images/inputs/main/', default=None)
    input_image_thumbnail = models.ImageField(upload_to='images/inputs/thumbnail/', default=None)

    output_image = models.ImageField(upload_to='images/outputs/main/', default=None)
    output_image_thumbnail = models.ImageField(upload_to='images/outputs/thumbnail/', default=None)

    def vote_feedback(self, value):
        self.owner_feedback = value
        if self.owner_feedback is not None and self.owner_feedback != value:
            value = value - self.owner_feedback
        self.save()
        self.server.update_avg_feedback()
        return 0, "Successful"

    def get_feedback_range(self):
        return range(self.owner_feedback)

    def create_thumbnails(self, related_list):
        # Relate list example: [(self.input_image, self.input_image_thumbnail)]
        for main_image, thum_image in related_list:
            image = Image.open(main_image.file)

            w, h = image.size
            ratio = w / 800
            image.thumbnail(size=(int(w / ratio), int(h / ratio)))

            image_file = BytesIO()
            image.save(image_file, image.format)

            thum_image.save(
                main_image.name + "_thumbnail",
                InMemoryUploadedFile(
                    image_file,
                    None, '',
                    main_image.file.content_type,
                    image.size,
                    main_image.file.charset,
                ),
                save=True
            )
        return True

    def clear_disk(self):
        f_path = os.path.join(app_setting.MEDIA_ROOT, self.input_file)
        if os.path.isfile(f_path):
            self.input_file = None
            os.remove(f_path)
        self.save()
        return True

    def add_applicant(self, designer):
        if not isinstance(designer, Designer):
            return 1, "Only designers can apply"

        if self.status != 'open':
            return 1, "This project is not open"

        if any(x.id == designer.id for x in self.applicants.all()):
            return 1, "Already applied"

        self.applicants.add(designer)
        self.save()
        return 0, "Successful"

    def approve_designer(self, designer):
        if not isinstance(designer, Designer):
            return 1, "Candidate should be a designer"

        if not self.server or self.server is not None:
            return 1, "Already has a candidate"

        if self.client.credit < designer.get_rate():
            return 2, "You need to charge your account to approve this designer. Please check your balance."

        self.server = designer
        self.status = 'progress'
        self.save()

        # TODO: Notify designer that he/she is approved
        r = designer.get_rate()
        self.client.charge(-r)
        self.server.charge((4*r)//5)

        self.server.score += 25
        self.server.save()

        return 0, "Successful"

    def is_visible(self, visitor):
        if self.allowed_to_share:
            return True

        if not isinstance(visitor, UserInfo):
            return False

        if isinstance(visitor, Client) and visitor.id == self.client.id:
            return True

        if isinstance(visitor, Designer):
            if self.status == "open" or (self.status == 'progress' and visitor.id == self.server.id):
                return True

        return False


class AdvancedProject(Project):
    input_file1 = models.FileField(upload_to='images/inputs/original_file', default=None)
    input_image1 = models.ImageField(upload_to='images/inputs/main/', default=None)
    input_image1_thumbnail = models.ImageField(upload_to='images/inputs/thumbnail/', default=None)

    input_file2 = models.FileField(upload_to='images/inputs/original_file', default=None)
    input_image2 = models.ImageField(upload_to='images/inputs/main/', default=None)
    input_image2_thumbnail = models.ImageField(upload_to='images/inputs/thumbnail/', default=None)

    input_file3 = models.FileField(upload_to='images/inputs/original_file', default=None)
    input_image3 = models.ImageField(upload_to='images/inputs/main/', default=None)
    input_image3_thumbnail = models.ImageField(upload_to='images/inputs/thumbnail/', default=None)

    input_file4 = models.FileField(upload_to='images/inputs/original_file', default=None)
    input_image4 = models.ImageField(upload_to='images/inputs/main/', default=None)
    input_image4_thumbnail = models.ImageField(upload_to='images/inputs/thumbnail/', default=None)

    def clear_disk(self):
        f_path = os.path.join(app_setting.MEDIA_ROOT, self.input_file)
        f_path1 = os.path.join(app_setting.MEDIA_ROOT, self.input_file1)
        f_path2 = os.path.join(app_setting.MEDIA_ROOT, self.input_file2)
        f_path3 = os.path.join(app_setting.MEDIA_ROOT, self.input_file3)
        f_path4 = os.path.join(app_setting.MEDIA_ROOT, self.input_file4)

        self.input_file = None
        self.input_file1 = None
        self.input_file2 = None
        self.input_file3 = None
        self.input_file4 = None

        for f_path in (f_path, f_path1, f_path2, f_path3, f_path4):
            if os.path.isfile(f_path):
                os.remove(f_path)

        self.save()
        return True


# ==================================================
# Storing all Payments, refunds and transactions here
# ==================================================
class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_date = models.TimeField(auto_now_add=True)
    user = models.ForeignKey(UserInfo, on_delete=models.SET_NULL, null=True, default=None)
    amount = models.IntegerField(default=0)
    reference = models.CharField(max_length=512, blank=True, null=True, default='')


class ProjectTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_date = models.TimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, default=None)
    company_benefit = models.IntegerField(default=0)
