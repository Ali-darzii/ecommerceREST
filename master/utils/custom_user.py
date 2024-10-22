from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
import re


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_no, password, **extra_fields):
        if not phone_no:
            raise ValueError(_("The Phone number must be set"))
        self.validate_phone_no(phone_no)
        user = self.model(phone_no=phone_no, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_no, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(phone_no, password, **extra_fields)

    def validate_phone_no(self, phone_no):
        if not re.match(r'^09\d{9}$', phone_no):
            ValueError(_("The Phone number is in bad format"))
        try:
            self.model.get(phone_no=phone_no, is_active=True)
            ValueError(_("Phone number already taken."))
        except Exception:
            pass
