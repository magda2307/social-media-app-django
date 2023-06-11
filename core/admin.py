from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from user.models import User

class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'bio']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('profile_picture', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    filter_horizontal = ()
    list_filter = ()
    exclude = ('username',)
admin.site.register(User, UserAdmin)
