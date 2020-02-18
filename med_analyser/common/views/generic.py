from django.shortcuts import redirect, render
from django.views.generic import TemplateView, DeleteView
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from ..models import Doctor

class HomePageView(TemplateView):
    template_name = 'home.html'

class SignUpView(TemplateView):
    template_name = 'account/signup.html'

class ProfileDeleteView(LoginRequiredMixin, View):
    model = Doctor
    template_name = "account/profile_delete.html"
    success_url = reverse_lazy('common:home')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.request.user
        self.object.delete()
        return HttpResponseRedirect(self.success_url)