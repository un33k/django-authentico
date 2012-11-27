from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from models import User
from forms import UserChangeForm
from forms import UserCreationForm
from backends import authenticate

class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'id')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'email', 'id')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

# Now Register the User
admin.site.register(User, UserAdmin)

