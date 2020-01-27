from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import DoctorSignUpForm
from django.contrib.auth import get_user_model
from .models import CustomUser, Doctor

admin.site.register(Doctor)