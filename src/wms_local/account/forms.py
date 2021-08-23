from django import forms
from django.contrib.auth import forms as django_forms, get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import pgettext

User = get_user_model()


class LoginForm(django_forms.AuthenticationForm):
    username = forms.CharField(
        label=pgettext('Form field', 'Username'), max_length=75,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": pgettext('Form field', 'Username')}))

    password = forms.CharField(
        label=pgettext('Form field', 'Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": pgettext('Form field', 'Password')}),
    )

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, request=request, **kwargs)
        if request:
            username = request.GET.get('username')
            if username:
                self.fields['username'].initial = username


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email',)
