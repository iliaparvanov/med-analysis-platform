from django import forms
from .models import Examination

class ExaminationUploadForm(forms.ModelForm):
  class Meta:
      model = Examination
      fields = ['pat_name', 'image', 'notes']

class ExaminationMarkNoFindingForm(forms.Form):
  no_finding = forms.BooleanField(required=False)

class ExaminationMarkFindingsForm(forms.Form):
  no_finding = forms.BooleanField(required=False)

