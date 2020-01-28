from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

class SubscriptionManageView(LoginRequiredMixin, TemplateView):
    template_name = 'subscriptions/manage.html'

class SubscriptionCheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'subscriptions/checkout.html'