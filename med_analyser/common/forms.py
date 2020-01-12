from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.db import transaction
from django import forms
from allauth.account.forms import SignupForm


from .models import CustomUser, Doctor, Hospital, CustomUser


class DoctorSignUpForm(SignupForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    def save(self, request):
        user = super(DoctorSignUpForm, self).save(request)

        doctor = Doctor(
            user=user,
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name')
        )
        doctor.save()

        return doctor.user

