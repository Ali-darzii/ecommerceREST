from django.contrib import admin
from . import models

admin.site.register(models.UserProfile)
admin.site.register(models.UserIP)
admin.site.register(models.UserLogins)
admin.site.register(models.UserDevice)
