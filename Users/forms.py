from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class  RegistrationForm(UserCreationForm):

    class Meta: 
        model = UserProfile
        fields = [ 'username', 'email', 'date_of_birth', 'password1']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
