from django.urls import path, include
from .views import *

app_name = 'subscriptions'
urlpatterns = [
    path('', SubscriptionManageView.as_view(), name='manage'),
]