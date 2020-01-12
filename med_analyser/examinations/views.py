from django.shortcuts import render
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Examination
from common.models import Doctor
import datetime

# Create your views here.
class ExaminationListView(ListView):
    model = Examination
    template_name = 'examinations/examination_list.html'

class ExaminationCreateView(LoginRequiredMixin, CreateView):
    model = Examination
    template_name = 'examinations/examination_new.html'
    fields = ['pat_name','notes',]

    def form_valid(self, form):
        form.instance.created_by = Doctor.objects.filter(user=self.request.user).first()
        form.instance.created_on = datetime.date.today()

        return super().form_valid(form)