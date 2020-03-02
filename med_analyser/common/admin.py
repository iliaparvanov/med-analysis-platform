from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import DoctorSignUpForm
from django.contrib.auth import get_user_model
from .models import CustomUser, Doctor, Hospital

admin.site.site_header = 'Medical Analysis Admin Dashboard'

class HospitalAdmin(admin.ModelAdmin):
    exclude=('subscription',)

admin.site.register(Doctor)
admin.site.register(Hospital, HospitalAdmin)