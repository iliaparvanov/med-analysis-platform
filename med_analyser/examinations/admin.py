from django.contrib import admin
from .models import Examination, ImageType, Finding, ConfirmedFinding, InferredFinding

admin.site.register(Examination)
admin.site.register(ImageType)
admin.site.register(Finding)
admin.site.register(ConfirmedFinding)
admin.site.register(InferredFinding)