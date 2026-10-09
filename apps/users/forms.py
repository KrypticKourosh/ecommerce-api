from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    '''Create User using Email instead of Username'''
    class Meta:
        model = User 
        fields = ('email',)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User 
        fields = '__all__'