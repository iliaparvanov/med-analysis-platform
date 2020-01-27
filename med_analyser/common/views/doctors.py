from django.contrib.auth import login
from django.shortcuts import redirect
from allauth.account.views import SignupView
from django.views.generic import CreateView
from subscriptions.models import Plan, Subscription

from ..forms import DoctorSignUpForm
from ..models import CustomUser
from django.conf import settings

class DoctorSignUpView(SignupView):
    template_name = 'account/signup_doctor.html'
    form_class = DoctorSignUpForm

