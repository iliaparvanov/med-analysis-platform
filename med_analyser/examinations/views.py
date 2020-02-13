from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DetailView, DeleteView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from braces.views import *
from .models import *
from .forms import *
from common.models import Doctor
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
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

class ExaminationMarkNoFindingView(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = Examination
    template_name = 'examinations/examination_mark_no_finding.html'
    form_class = ExaminationMarkNoFindingForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def form_valid(self, form):
        print(form.cleaned_data)
        if form.cleaned_data['no_finding']:
            # add to confirmed findings, display message, redirect back to examination
            try:
                cf = ConfirmedFinding(finding=Finding.objects.filter(is_no_finding=True, inferredfinding__in=InferredFinding.objects.filter(examination=self.get_object())).first(), examination=self.get_object())
                cf.save()
            except:
                raise Http404('Error')
            messages.add(self.request, messages.SUCCESS, 'Successfuly marked correct diagnosis!')
            return redirect('examination_detail', pk=self.get_object().pk)
        # go to next view
        return redirect('examination_mark_findings', pk=self.get_object().pk)

class ExaminationMarkFindingsView(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = Examination
    template_name = 'examinations/examination_mark_findings.html'
    form_class = ExaminationMarkFindingsForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def form_valid(self, form):
        print(form.cleaned_data)
        return HttpResponseRedirect('/')
    
