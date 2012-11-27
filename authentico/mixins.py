# taken out of django/contrib/auth/models.py
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import Permission
from django.core.mail import send_mail
from django.utils import timezone
from django.db import models

from util import get_uuid

class LowerCaseEmailField(models.EmailField):
    """Email is case insensitive"""
    def get_prep_value(self, value):
        value = super(LowerCaseEmailField, self).get_prep_value(value)
        return value.lower()


# A few helper functions for common logic between User and AnonymousUser.
def _user_get_all_permissions(user, obj):
    permissions = set()
    for backend in auth.get_backends():
        if hasattr(backend, "get_all_permissions"):
            if obj is not None:
                permissions.update(backend.get_all_permissions(user, obj))
            else:
                permissions.update(backend.get_all_permissions(user))
    return permissions


def _user_has_perm(user, perm, obj):
    for backend in auth.get_backends():
        if hasattr(backend, "has_perm"):
            if obj is not None:
                if backend.has_perm(user, perm, obj):
                    return True
            else:
                if backend.has_perm(user, perm):
                    return True
    return False


def _user_has_module_perms(user, app_label):
    for backend in auth.get_backends():
        if hasattr(backend, "has_module_perms"):
            if backend.has_module_perms(user, app_label):
                return True
    return False



class UserPermissionsMixin(models.Model):
    """A mixin that handles permissions for User"""

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('If true, then this user can log into this admin site.')
    )
                    
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_('If true, then this user has unrestricted permissions')
    )
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will '
                    'get all permissions granted to each of '
                    'his/her group.')
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'), 
        blank=True,
        help_text='Specific permissions for this user.'
    )

    class Meta:
        abstract = True

    def get_group_permissions(self, obj=None):
        """
        Returns a list of permission strings that this user has through his/her
        groups. This method queries all available auth backends. If an object
        is passed in, only permissions matching this object are returned.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                if obj is not None:
                    permissions.update(backend.get_group_permissions(self,
                                                                     obj))
                else:
                    permissions.update(backend.get_group_permissions(self))
        return permissions

    def get_all_permissions(self, obj=None):
        return _user_get_all_permissions(self, obj)

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the specified permissions. If
        object is passed, it checks if the user has all required perms for this
        object.
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)



class UserBasicMixin(models.Model):
    """
    An abstract base class implementing a basic User model.
    Email and password are required. Other fields are optional.
    """
    id = models.CharField(
        primary_key=True,
        editable=False,
        db_index=True,
        max_length=32,
        default=get_uuid(),
    )

    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now
    )

    email = LowerCaseEmailField(
        _('email address'),
        blank=False,
        unique=True,
    )

    first_name = models.CharField(
        _('first name'),
        max_length=50,
        blank=True,
    )
    
    last_name = models.CharField(
        _('last name'),
        max_length=50,
        blank=True,
    )
    
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('If true, then this user is active'),
    )

    is_public = models.BooleanField(
        _('public'),
        default=True,
        help_text=_('If true, then this user is public'),
    )
    
    class Meta:
        abstract = True

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.uuid)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])


class UserExternalProfileMixin(models.Model):
    """
    An abstract base class implementing an external profile support
    """

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        warnings.warn("The use of AUTH_PROFILE_MODULE to define user profiles has been deprecated.",
            PendingDeprecationWarning)
        if not hasattr(self, '_profile_cache'):
            from django.conf import settings
            if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
                raise SiteProfileNotAvailable(
                    'You need to set AUTH_PROFILE_MODULE in your project '
                    'settings')
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            except ValueError:
                raise SiteProfileNotAvailable(
                    'app_label and model_name should be separated by a dot in '
                    'the AUTH_PROFILE_MODULE setting')
            try:
                model = models.get_model(app_label, model_name)
                if model is None:
                    raise SiteProfileNotAvailable(
                        'Unable to load the profile model, check '
                        'AUTH_PROFILE_MODULE in your project settings')
                self._profile_cache = model._default_manager.using(
                                   self._state.db).get(user__id__exact=self.id)
                self._profile_cache.user = self
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return self._profile_cache


class UserBasicExternalProfileMixin(UserBasicMixin, UserExternalProfileMixin, UserPermissionsMixin):
    # support external profile
    pass




