from django.urls import path, include

from django.contrib.auth import views as auth_views
from . import views
from .views import generic, doctors, hospitals

app_name = 'common'
urlpatterns = [
    # path('accounts/login/', auth_views.LoginView.as_view(template_name='accounts/login.html')),
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('accounts/signup/', generic.SignUpView.as_view(), name='signup'),
    # path('accounts/signup/doctor/', doctors.DoctorSignUpView.as_view(), name='doctor_signup'),
    # path('accounts/profile/', generic.ProfileView.as_view(), name='profile'),
    path('', generic.HomePageView.as_view(), name='home'),
    path('accounts/signup/doctors', doctors.DoctorSignUpView.as_view(), name='doctor_signup'),
    # path('accounts/signup/hospital/', hospitals.HospitalSignUpView.as_view(), name='hospital_signup'),
]