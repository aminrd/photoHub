# Generated by Django 3.0.5 on 2020-04-10 01:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('target_deadline', models.DateTimeField(default=None)),
                ('time_finished', models.DateTimeField(default=None)),
                ('status', models.CharField(choices=[('open', 'Open'), ('progress', 'Already Assigned'), ('finished', 'Finished')], default='open', max_length=16)),
                ('allowed_to_share', models.BooleanField(blank=True, default=False, null=True)),
                ('report_on_portfolio', models.BooleanField(default=True)),
                ('description', models.TextField(default='', max_length=2048)),
                ('owner_feedback', models.IntegerField(default=None)),
                ('owner_feedback_text', models.TextField(blank=True, default='', max_length=512, null=True)),
                ('price_spend', models.IntegerField(default=1)),
                ('input_file', models.FileField(default=None, upload_to='images/inputs/original_file')),
                ('input_image', models.ImageField(default=None, upload_to='images/inputs/main/')),
                ('input_image_thumbnail', models.ImageField(default=None, upload_to='images/inputs/thumbnail/')),
                ('output_image', models.ImageField(default=None, upload_to='images/outputs/main/')),
                ('output_image_thumbnail', models.ImageField(default=None, upload_to='images/outputs/thumbnail/')),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('default_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('role', models.CharField(default='user_info', max_length=16)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('activated', models.BooleanField(blank=True, default=False, null=True)),
                ('verified', models.BooleanField(default=False)),
                ('credit', models.IntegerField(default=0)),
                ('has_profile_picture', models.BooleanField(default=False)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_images/main/')),
                ('profile_thumbnail', models.ImageField(blank=True, null=True, upload_to='profile_images/thumbnail/')),
            ],
        ),
        migrations.CreateModel(
            name='AdvancedProject',
            fields=[
                ('project_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='WebApplication.Project')),
                ('input_file1', models.FileField(default=None, upload_to='images/inputs/original_file')),
                ('input_image1', models.ImageField(default=None, upload_to='images/inputs/main/')),
                ('input_image1_thumbnail', models.ImageField(default=None, upload_to='images/inputs/thumbnail/')),
                ('input_file2', models.FileField(default=None, upload_to='images/inputs/original_file')),
                ('input_image2', models.ImageField(default=None, upload_to='images/inputs/main/')),
                ('input_image2_thumbnail', models.ImageField(default=None, upload_to='images/inputs/thumbnail/')),
                ('input_file3', models.FileField(default=None, upload_to='images/inputs/original_file')),
                ('input_image3', models.ImageField(default=None, upload_to='images/inputs/main/')),
                ('input_image3_thumbnail', models.ImageField(default=None, upload_to='images/inputs/thumbnail/')),
                ('input_file4', models.FileField(default=None, upload_to='images/inputs/original_file')),
                ('input_image4', models.ImageField(default=None, upload_to='images/inputs/main/')),
                ('input_image4_thumbnail', models.ImageField(default=None, upload_to='images/inputs/thumbnail/')),
            ],
            bases=('WebApplication.project',),
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('userinfo_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='WebApplication.UserInfo')),
            ],
            bases=('WebApplication.userinfo',),
        ),
        migrations.CreateModel(
            name='Designer',
            fields=[
                ('userinfo_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='WebApplication.UserInfo')),
                ('score', models.IntegerField(default=0)),
                ('avg_feedback', models.DecimalField(decimal_places=1, default=0.0, max_digits=3)),
                ('rate', models.IntegerField(default=100)),
                ('user_plus', models.BooleanField(default=False)),
                ('user_plus_expires', models.DateTimeField(auto_now_add=True)),
                ('homepage_link', models.CharField(blank=True, default=None, max_length=1024, null=True)),
                ('instagram_url', models.CharField(blank=True, default=None, max_length=1024, null=True)),
                ('linkedin_url', models.CharField(blank=True, default=None, max_length=1024, null=True)),
            ],
            bases=('WebApplication.userinfo',),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transaction_date', models.TimeField(auto_now_add=True)),
                ('amount', models.IntegerField(default=0)),
                ('reference', models.CharField(blank=True, default='', max_length=512, null=True)),
                ('user', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='WebApplication.UserInfo')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectTransaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transaction_date', models.TimeField(auto_now_add=True)),
                ('company_benefit', models.IntegerField(default=0)),
                ('project', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='WebApplication.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Notificatino',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('read', models.BooleanField(default=False)),
                ('content', models.TextField(max_length=512)),
                ('link', models.TextField(default=None, max_length=512)),
                ('related_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_key', to='WebApplication.UserInfo')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='applicants',
            field=models.ManyToManyField(to='WebApplication.Designer'),
        ),
        migrations.AddField(
            model_name='project',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_client', to='WebApplication.Client'),
        ),
        migrations.AddField(
            model_name='project',
            name='server',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_server', to='WebApplication.Designer'),
        ),
    ]
