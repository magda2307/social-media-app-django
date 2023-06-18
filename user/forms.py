from django import forms
from user.models import User
MAX_EMAIL_LENGTH = 100

class UserRegistration(forms.ModelForm):
    email = forms.EmailField(max_length=MAX_EMAIL_LENGTH)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email','password']
