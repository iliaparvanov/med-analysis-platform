from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Examination
from .forms import ExaminationUploadForm
from common.models import Doctor
from django.urls import reverse_lazy
import datetime

from .apps import ExaminationsConfig
from fastai.vision.image import open_image 

def get_doctor(request):
    return Doctor.objects.filter(user=request.user).first()

# Create your views here.
class ExaminationListView(LoginRequiredMixin, ListView):
    login_url = 'account_login'
    template_name = 'examinations/examination_list.html'
    context_object_name = 'examinations'
    def get_queryset(self):
        return Examination.objects.filter(created_by=get_doctor(self.request)).order_by('created_on')

class ExaminationDetailView(LoginRequiredMixin, DetailView):
    login_url = 'account_login'
    model = Examination
    context_object_name = 'examination'
    template_name = 'examinations/examination_detail.html'

class ExaminationCreateView(LoginRequiredMixin, CreateView):
    login_url = 'account_login'
    form_class = ExaminationUploadForm
    template_name = 'examinations/examination_new.html'

    def form_valid(self, form):
        form.instance.created_by = get_doctor(self.request)
        form.instance.created_on = datetime.date.today()
        img = open_image(form.instance.image.file)
        pred_class,pred_idx,outputs = ExaminationsConfig.learner_image_type.predict(img)
        form.instance.examination_type = str(pred_class)
        
        return super().form_valid(form)

class ExaminationDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'account_login'
    model = Examination
    template_name = 'examinations/examination_delete.html'
    success_url = reverse_lazy('examination_list')