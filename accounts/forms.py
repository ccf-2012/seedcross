from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
# https://stackoverflow.com/questions/55369645/how-to-customize-default-auth-login-form-in-django/55369791
from django import forms
from django.forms.fields import CharField
from django.forms.widgets import PasswordInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML, Div
from crispy_forms.bootstrap import PrependedText


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())

    # helper = FormHelper()
    # # helper.form_class = 'form-horizontal'
    # helper.label_class = 'col-lg-2'
    # helper.field_class = 'col-lg-4'
    # helper.layout = Layout(
    #     'username',
    #     'password',
    #     Submit('submit', 'Login'),
    # )


# https://stackoverflow.com/questions/35256802/how-to-implement-password-change-form-in-django-1-9
class PasswordChangeCustomForm(PasswordChangeForm):
    error_css_class = 'has-error'
    error_messages = {'password_incorrect': "input password"}
    old_password = CharField(
        required=True,
        label='Current Password',
        widget=PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Input old password'})

    new_password1 = CharField(
        required=True,
        label='New Password',
        widget=PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Please input New Pasword'})
    new_password2 = CharField(
        required=True,
        label='New Password (Confirm)',
        widget=PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Please input New Pasword'})

    helper = FormHelper()
    # helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-3'
    helper.field_class = 'col-lg-6'
    helper.layout = Layout(
        'old_password',
        'new_password1',
        'new_password2',
        Submit('submit', 'Change Password'),
    )

