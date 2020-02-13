from django import forms
from .models import Examination


class ExaminationUploadForm(forms.ModelForm):
    class Meta:
        model = Examination
        fields = ['pat_name', 'image', 'notes']


class ExaminationMarkNoFindingForm(forms.Form):
    no_finding = forms.BooleanField(required=False)


class ExaminationMarkFindingsForm(forms.Form):
    findings = forms.MultipleChoiceField(
        required=True, widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        self.findings_choices = kwargs.pop('findings_choices')
        super(ExaminationMarkFindingsForm, self).__init__(*args, **kwargs)
        self.fields['findings'].choices = self.findings_choices
        self.fields['findings'].error_messages = {'required': 'Please mark at least one finding. If there were no findings, go back to the previous page.'}
