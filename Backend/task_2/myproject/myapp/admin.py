from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Organisation

# Register your models here.
class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'firstName', 'lastName', 'phone')

class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'firstName', 'lastName', 'phone', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')

class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('userId', 'email', 'firstName', 'lastName', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('firstName', 'lastName', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstName', 'lastName', 'phone', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )
    search_fields = ('email', 'firstName', 'lastName', 'phone')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('orgId', 'name', 'description')
    search_fields = ('orgId', 'name')

admin.site.register(User, UserAdmin)
admin.site.register(Organisation, OrganisationAdmin)
