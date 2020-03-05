from django.db import models
from django.contrib.auth.models import User


# Third-party libraries
from phonenumber_field.modelfields import PhoneNumberField

# Image and Thumbnail related libraries
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


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


class Client(UserInfo):
    # List of projects: client_project <list>
    pass

class Designer(UserInfo):
    score = models.IntegerField(default=0)
    avg_feedback = models.DecimalField(max_digits=3, decimal_places=1 ,default=0.0)
    rate = models.IntegerField(default=1)

# ==================================================
# Define User, Client and Designer tables
# ==================================================
class Project(models.Model):

    PROJECT_STATUS = [
        ("open", 'Open'),
        ("progress", 'Sophomore'),
        ("finished", 'Finished'),
    ]

    date_created = models.DateTimeField(auto_now_add=True)
    target_deadline = models.DateTimeField(default=None)
    time_finished = models.DateTimeField(default=None)
    status = models.CharField(max_length=16, choices=PROJECT_STATUS, default="open")

    # Users related
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name='project_client')
    server = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name='project_server', default=None)
    applicants = models.ManyToManyField(Designer)

    report_on_portfolio = models.BooleanField(default=True)
    description = models.TextField(max_length=2048, default="")

    # Could be None, 1,2,3,4,5
    owner_feedback = models.IntegerField(default=None)
    price_spend = models.IntegerField(default=0)

    input_image = models.ImageField(upload_to='images/inputs/main/', default=None)
    input_image_thumbnail = models.ImageField(upload_to='images/inputs/thumbnail/', default=None)

    output_image = models.ImageField(upload_to='images/outputs/main/', default=None)
    output_image_thumbnail = models.ImageField(upload_to='images/outputs/thumbnail/', default=None)

    def create_thumbnails(self, related_list):
        # Relate list example: [(self.input_image, self.input_image_thumbnail)]
        for main_image, thum_image in related_list:
            image = Image.open(main_image.file)

            w,h = image.size
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


class AdvancedProject(Project):
    input_image1 = models.ImageField(upload_to='images/inputs/main/', default=None)
    input_image1_thumbnail = models.ImageField(upload_to='images/inputs/thumbnail/', default=None)
    input_image2 = models.ImageField(upload_to='images/inputs/main/', default=None)
    input_image2_thumbnail = models.ImageField(upload_to='images/inputs/thumbnail/', default=None)
    input_image3 = models.ImageField(upload_to='images/inputs/main/', default=None)
    input_image3_thumbnail = models.ImageField(upload_to='images/inputs/thumbnail/', default=None)
    input_image4 = models.ImageField(upload_to='images/inputs/main/', default=None)
    input_image4_thumbnail = models.ImageField(upload_to='images/inputs/thumbnail/', default=None)
