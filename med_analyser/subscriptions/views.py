from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class SubscriptionManageView(TemplateView):
    template_name = 'subscriptions/manage.html'