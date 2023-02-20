from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Follow


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    search_fields = ('email', 'username', 'first_name', 'last_name')
    fieldsets = (
        (
            None,
            {'fields': ('username', 'password')}
        ),
        (
            'Персональные данные',
            {'fields': ('first_name', 'last_name', 'email')}
        ),
        (
            'Права',
            {
                'fields': ('is_active', 'is_staff', 'is_superuser'),
            }
        ),
        (
            'Даты',
            {'fields': ('last_login', 'date_joined')}
        ),
    )
    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': ('username',
                           'password1',
                           'password2',
                           'email',
                           'first_name',
                           'last_name',),
            }
        ),
    )


admin.register(Follow)
