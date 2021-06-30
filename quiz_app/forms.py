import pytz
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.models import ModelChoiceField

from .models import Account, Quiz


class QuizForm(forms.Form):
    email = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter Email",
            }
        ),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter Password",
            }
        ),
    )
    key = forms.CharField(
        max_length=8,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter Your Quiz-ID",
                
            }
        ),
    )

    class Meta:
        model = Quiz
        fields = ["key"]


class QuizAddFormStaff(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuizAddFormStaff, self).__init__(*args, **kwargs)
        self.fields["invigilator"].widget = forms.HiddenInput()
        self.fields["invigilator"].widget.attrs["disabled"] = "True"

    invigilator = ModelChoiceField(
        queryset=Account.objects.filter(is_staff=True).all(), required=False,
    )

    class Meta:
        model = Quiz
        fields = "__all__"


class SignUpForm(UserCreationForm):
    timeZone = forms.ChoiceField(
        initial="UTC",
        choices=[(tz, tz) for tz in pytz.common_timezones],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Account
        fields = ("full_name", "email", "timeZone")
