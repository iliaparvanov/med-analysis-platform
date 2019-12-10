from django.urls import path, include

from . import views
from .views import generic, doctors, hospitals

app_name = 'common'
urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', generic.SignUpView.as_view(), name='signup'),
    path('accounts/signup/doctor/', doctors.DoctorSignUpView.as_view(), name='doctor_signup'),
    # path('accounts/signup/hospital/', hospitals.HospitalSignUpView.as_view(), name='hospital_signup'),
]