from django.urls import path, include

from django.contrib.auth import views as auth_views
from . import views
from .views import generic, doctors, hospitals

app_name = 'common'
urlpatterns = [
    path('', generic.HomePageView.as_view(), name='home'),
    path('accounts/signup/doctors', doctors.DoctorSignUpView.as_view(), name='doctor_signup'),
    path('accounts/doctor', doctors.DoctorDetailView.as_view(), name='doctor_detail')
]