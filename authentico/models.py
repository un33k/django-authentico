from django.contrib.auth.models import UserManager as DjangoUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import models

from mixins import UserBasicMixin
from mixins import UserPermissionsMixin

class UserManager(DjangoUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError(_('Users must have an email address.'))

        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        su = self.create_user(email, password, **extra_fields)
        su.is_staff = True
        su.is_active = True
        su.is_superuser = True
        su.save(using=self._db)
        return su


class User(AbstractBaseUser, UserBasicMixin, UserPermissionsMixin):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()





