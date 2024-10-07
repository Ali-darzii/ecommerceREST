import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import SET_NULL
from django.contrib.auth.validators import UnicodeUsernameValidator as username_validator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        blank=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )


class PhoneMessage(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=SET_NULL,
        related_name='phone_message',
        null=True,
        blank=True
    )
    token = models.CharField(max_length=6, null=True)
    expiration_time = models.DateTimeField()
    phone_no = models.CharField(max_length=11, unique=True)

    def __str__(self):

        try:
            return self.user.username + '_phone'
        except:
            return self.phone_no + '_phone_message'

    class Meta:
        db_table = 'PhoneMessage_DB'
        verbose_name = 'User PhoneMessage'
        verbose_name_plural = 'Users PhoneMessage'

    def set_tk(self):
        self.token = random.randrange(1000, 9999)
        self.save()

    def set_expiration_time(self):
        self.expiration_time = timezone.now() + timedelta(minutes=5)
        self.save()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profiles')
    avatar = models.ImageField(upload_to='../images/avatar', null=True)
    address = models.TextField(null=True)
    city = models.CharField(max_length=100, null=True)
    postal_code = models.IntegerField(null=True)

    # todo:phone

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
