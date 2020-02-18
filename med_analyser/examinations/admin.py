from django.contrib import admin
from .models import Examination, ImageType, Finding, ConfirmedFinding

admin.site.register(Examination)
admin.site.register(ImageType)
admin.site.register(Finding)
admin.site.register(ConfirmedFinding)