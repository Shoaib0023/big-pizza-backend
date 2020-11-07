from django import forms
from .models import UserProfile


class LoginForm(forms.Form):
    class Meta:
        model = UserProfile
        fields = ('phone',)

