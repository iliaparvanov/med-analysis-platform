from django.contrib.auth import login
from django.shortcuts import redirect
from allauth.account.views import SignupView
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from subscriptions.models import Plan, Subscription

from ..forms import DoctorSignUpForm
from ..models import CustomUser, Doctor
from django.conf import settings

class DoctorSignUpView(SignupView):
    template_name = 'account/signup_doctor.html'
    form_class = DoctorSignUpForm

class DoctorDetailView(LoginRequiredMixin, DetailView):
    model = Doctor
    context_object_name = 'doctor'
    template_name = 'account/detail_doctor.html'

    def get_object(self, queryset=None):
        obj = self.request.user.doctor
        return obj

    

