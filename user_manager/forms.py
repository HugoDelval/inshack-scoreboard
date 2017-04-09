from collections import OrderedDict

from django import forms
from django.contrib.auth.models import User

from user_manager.models import TeamProfile


class TeamProfileForm(forms.ModelForm):
    class Meta:
        model = TeamProfile

        #  on_site removed because we should add the teams directly
        # during the event, that way, no "cheating"
        fields = ['comes_from', 'avatar', 'wants_to_be_contacted']

    def __init__(self, *args, **kwargs):
        super(TeamProfileForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].label = "A fun GIF! -> http://giphy.com/"
        self.fields['avatar'].widget.attrs.update({
            'class': 'form-control validate',
        })

        self.fields['comes_from'].label = 'Where are you coming from?'
        self.fields['comes_from'].widget.attrs.update({
            'class': 'form-control validate',
        })

        self.fields['wants_to_be_contacted'].label = 'Do you want to be contacted by our partners? (e.g. for a employment)'

        self.fields = OrderedDict((k, self.fields[k]) for k in self.fields)

    def clean_avatar(self):
        image = self.cleaned_data.get('avatar')
        if "insecurity-insa.fr" in image:
            raise forms.ValidationError('I want a gif!')
        return image


class UserForm(forms.ModelForm):
    password_validation = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Team name'
        self.fields['username'].widget.attrs.update({
            'class': 'form-control validate',
        })

        self.fields['email'].label = 'Team email'
        self.fields['email'].widget = forms.EmailInput()
        self.fields['email'].widget.attrs.update({
            'class': 'form-control validate',
        })

        self.fields['password'].label = 'Password'
        self.fields['password'].widget = forms.PasswordInput()
        self.fields['password'].widget.attrs.update({
            'class': 'form-control validate',
        })

        self.fields['password_validation'].label = 'Password verification'
        self.fields['password_validation'].widget = forms.PasswordInput()
        self.fields['password_validation'].widget.attrs.update({
            'class': 'form-control validate',
        })

        if self.instance.pk is not None:
            self.fields['password_validation'].required = False
            self.fields['password_validation'].label = 'New password verification'
            self.fields['password'].required = False
            self.fields['password'].label = 'New password'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('An email is required')
        elif (self.instance and User.objects.filter(email=email).exclude(id=self.instance.id).count() != 0) or \
                (not self.instance and User.objects.filter(email=email).count() != 0):
            raise forms.ValidationError('An account using this email already exists.')
        return email

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        password_validation = cleaned_data.get("password_validation")
        if password or password_validation:
            if password_validation != password:
                error = "Passwords don't match."
                raise forms.ValidationError(error)
        return cleaned_data


class LoginForm(forms.Form):
    username_or_email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields['username_or_email'].label = 'Team name or email'
        self.fields['username_or_email'].widget.attrs.update({
            'class': 'form-control validate',
        })

        self.fields['password'].label = 'Password'
        self.fields['password'].widget.attrs.update({
            'class': 'form-control validate'
        })
