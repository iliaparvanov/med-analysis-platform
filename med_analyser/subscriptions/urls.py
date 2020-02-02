from django.urls import path, include
from .views import *

app_name = 'subscriptions'
urlpatterns = [
    path('', SubscriptionManageView.as_view(), name='manage'),
    path('checkout/<str:plan_type>/', SubscriptionCheckoutView.as_view(), name='checkout'),

    path('checkout/success', SubscriptionCheckoutSuccessView.as_view(), name='checkout_success')
]