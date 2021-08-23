from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.admin import UserAdmin

from .account.models import User
from .account.forms import CustomUserCreationForm, CustomUserChangeForm


admin.site.site_header = "WMS Local"
admin.site.site_title = "WMS"
admin.site.index_title = "WMS LOCAL"


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('username', 'email', 'is_staff', 'is_active')
    fieldsets = (
        ('Infomation', {'fields': ('username', 'password', 'email', 'full_name', 'mobile_number')}),
        ('Permissions', {'fields': ('user_permissions', 'groups')}),
        ('Status', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
        ('Infomation', {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'mobile_number')}
         ),
    )
    search_fields = ('username',)
    ordering = ('username',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Permission)
admin.site.register(ContentType)
