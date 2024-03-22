from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Client)
admin.site.register(Designer)
admin.site.register(Project)
admin.site.register(AdvancedProject)
admin.site.register(Notification)
