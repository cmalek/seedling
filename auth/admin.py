from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_active',
        'is_staff',
        'is_superuser'
    )
    list_display_links = ('username', 'first_name', 'last_name')
    search_fields = ('first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser')


admin.site.register(User, UserAdmin)
