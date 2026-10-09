from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm # UserAdmin uses username field by default
    form = CustomUserChangeForm

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', )}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        (None, {'fields': ('date_joined', )}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2')}),
    )