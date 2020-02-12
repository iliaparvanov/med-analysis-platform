from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, DeleteView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from braces.views import *
from .models import Examination, ImageType, InferredFinding, Finding
from .forms import *
from common.models import Doctor
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseRedirect
import datetime

from .apps import ExaminationsConfig
from fastai.vision.image import open_image 

# Create your views here.
class ExaminationListView(LoginRequiredMixin, ListView):
    template_name = 'examinations/examination_list.html'
    context_object_name = 'examinations'
    def get_queryset(self):
        return Examination.objects.filter(created_by=self.request.user.doctor).order_by('created_on')

class ExaminationDetailView(LoginRequiredMixin, DetailView):
    model = Examination
    context_object_name = 'examination'
    template_name = 'examinations/examination_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        findings = InferredFinding.objects.filter(examination=self.get_object())
        context['inferred_findings'] = findings
        return context

class ExaminationCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    def exceeded_max_examinations_redirect(self, request):
            messages.add_message(request, messages.INFO, 'You\'ve exceeded the maximum number of examinations! Please delete an existing examination or get a higher tier subscription.')
            return HttpResponseRedirect(reverse_lazy('subscriptions:manage'))

    raise_exception = exceeded_max_examinations_redirect
    redirect_unauthenticated_users = True
    form_class = ExaminationUploadForm
    template_name = 'examinations/examination_new.html'

    def test_func(self, user):
        return user.doctor.can_create_more_examinations

    def form_valid(self, form):
        form.instance.created_by = self.request.user.doctor
        form.instance.created_on = datetime.date.today()

        img = open_image(form.instance.image.file)
        pred_class,pred_idx,outputs = ExaminationsConfig.learner_image_type.predict(img)
        form.instance.image_type = ImageType.objects.get(label=str(pred_class))

        return super().form_valid(form)

class ExaminationDeleteView(LoginRequiredMixin, DeleteView):
    model = Examination
    template_name = 'examinations/examination_delete.html'
    success_url = reverse_lazy('examination_list')

class ExaminationMarkDefectNoFindingView(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = Examination
    template_name = 'examinations/examination_mark_defect_no_finding.html'
    form_class = ExaminationMarkDefectNoFindingForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def form_valid(self, form):
        print(form.cleaned_data)
        return HttpResponseRedirect('/')