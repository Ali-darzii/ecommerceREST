from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.custom_user import CustomUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.contrib.auth import user_logged_in
from utils.utils import get_client_ip

login_failed = Signal(providing_args=["request", "user"])



class User(AbstractUser):
    username = None
    phone_no = models.CharField(_("phone number"), unique=True, max_length=11, db_index=True)
    email_activate = models.BooleanField(default=False)
    USERNAME_FIELD = "phone_no"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.phone_no

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "User_DB"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profiles')
    avatar = models.ImageField(upload_to='images/avatar', null=True)
    address = models.TextField(null=True)
    city = models.CharField(max_length=100, null=True)
    postal_code = models.IntegerField(null=True)

    def __str__(self):
        return str(self.user.first_name) + '_profile'

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
    def get_user_device(cls, user_agent, user_logins_id):
        return cls(device_name=user_agent["device_name"], is_phone=user_agent["is_phone"],
                   browser=user_agent["browser"], os=user_agent["os"], user_logins_id=user_logins_id)

    def __str__(self):
        return str(self.user_logins.user.first_name) + '_device'

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


@receiver(signal=login_failed)
def add_user_failed_ip(sender, request, user, **kwargs):
    """update user_logins data if failed"""
    ip = UserIP(user_logins=user.user_logins, ip=get_client_ip(request), failed=True)
    user.user_logins.failed_attempts += 1
    user.user_logins.save()
    ip.save()


login_failed.connect(add_user_failed_ip)