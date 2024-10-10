from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    username = None
    phone_no = models.CharField(_("phone number"), unique=True)
    USERNAME_FIELD = "phone_no"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profiles')
    avatar = models.ImageField(upload_to='../images/avatar', null=True)
    address = models.TextField(null=True)
    city = models.CharField(max_length=100, null=True)
    postal_code = models.IntegerField(null=True)

    def __str__(self):
        return str(self.user.first_name) + '_profile'

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'Users Profiles'
        db_table = 'UserProfile_DB'


class UserLogins(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_logins')
    no_logins = models.PositiveIntegerField(default=0)
    failed_attempts = models.PositiveIntegerField(default=0)

    # no_devices = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.user.first_name + '_logins'

    class Meta:
        verbose_name = 'User Login'
        verbose_name_plural = 'User Logins'
        db_table = 'UserLogins_DB'


class UserIP(models.Model):
    user_logins = models.ForeignKey(UserLogins, on_delete=models.CASCADE, related_name='ips')
    ip = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now_add=True)
    failed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user_logins.user.first_name) + '_ip'

    class Meta:
        verbose_name = 'User IPs'
        verbose_name_plural = 'User IP'
        db_table = 'UserIP_DB'


class UserDevice(models.Model):
    user_logins = models.ForeignKey(UserLogins, on_delete=models.CASCADE, related_name='devices')
    device_name = models.CharField(max_length=100)
    is_phone = models.BooleanField(default=False)
    browser = models.CharField(max_length=100)
    os = models.CharField(max_length=100)

    @classmethod
    def get_user_device(cls, request, user):
        device_name = request.user_agent.device.family
        is_phone = request.user_agent.is_mobile
        browser = request.user_agent.browser.family
        os = request.user_agent.os.family
        return cls(device_name=device_name, is_phone=is_phone, browser=browser, os=os, user_logins=user.user_logins)

    def __str__(self):
        return str(self.user_logins.user.first_name) + '_device'

    class Meta:
        verbose_name = 'User Devices'
        verbose_name_plural = 'User Device'
        db_table = 'UserDevice_DB'
