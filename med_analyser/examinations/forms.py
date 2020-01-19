from django.forms import ModelForm   
from .models import Examination

class ExaminationUploadForm(ModelForm):
  class Meta:
      model = Examination
      fields = ['pat_name', 'image', 'notes']
