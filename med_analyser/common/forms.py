from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db import transaction
from django import forms

from .models import CustomUser, Doctor, Hospital, CustomUser


class DoctorSignUpForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = '__all__'

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_doctor = True
        user.save()
        doctor = Doctor.objects.create(user=user, email=self.cleaned_data.get('email'), first_name=self.cleaned_data.get('first_name'), last_name=self.cleaned_data.get('last_name'))
        # student.interests.add(*self.cleaned_data.get('interests'))
        return user

class DoctorChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'
