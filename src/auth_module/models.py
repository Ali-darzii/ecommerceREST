from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.custom_user import CustomUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import user_logged_in, user_login_failed
from utils.utils import get_client_ip


class User(AbstractUser):
    username = None
    phone_no = models.CharField(_("phone number"), unique=True, max_length=11, db_index=True)
    USERNAME_FIELD = "phone_no"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    @property
    def email_activate(self):
        return True if self.email else False

    @property
    def avatar(self):
        return self.user_profile.avatar


    def __str__(self):
        return self.phone_no

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "User_DB"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    avatar = models.ImageField(upload_to='images/avatar', null=True)
    address = models.TextField(null=True)
    city = models.CharField(max_length=100, null=True)
    postal_code = models.IntegerField(null=True)

    def __str__(self):
        return str(self.user.phone_no) + '_profile'

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'Users Profiles'
        db_table = 'UserProfile_DB'


# user data analyze

class UserLogins(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_logins')
    no_logins = models.PositiveIntegerField(default=0)
    failed_attempts = models.PositiveIntegerField(default=0)

    # no_devices = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.user.phone_no + '_logins'

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
        return str(self.user_logins.user.phone_no) + '_ip'

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
        return str(self.user_logins.user.phone_no) + '_device'

    class Meta:
        verbose_name = 'User Devices'
        verbose_name_plural = 'User Device'
        db_table = 'UserDevice_DB'


@receiver(signal=post_save, sender=User)
def create_user_logins(sender, created, instance, **kwargs):
    """create user_logins obj after user created"""
    if created and isinstance(instance, User):
        UserLogins.objects.create(user=instance)


@receiver(signal=user_logged_in)
def add_user_ip(sender, request, user, **kwargs):
    """add user ip after user logged in"""
    ip = UserIP(user_logins=user.user_logins, ip=get_client_ip(request))
    user.user_logins.no_logins += 1
    user.user_logins.save()
    ip.save()


@receiver(signal=user_logged_in)
def add_user_device(sender, request, user, **kwargs):
    """add user device after user logged in"""
    device = UserDevice.get_user_device(request, user)
    device.save()


@receiver(signal=user_login_failed)
def add_user_failed_ip(sender, request, user, **kwargs):
    """update user_logins data if failed"""
    ip = UserIP(user_logins=user.user_logins, ip=get_client_ip(request), failed=True)
    user.user_logins.failed_attempts += 1
    user.user_logins.save()
    ip.save()
