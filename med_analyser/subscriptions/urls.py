from django.urls import path, include
from .views import *

app_name = 'subscriptions'
urlpatterns = [
    path('', SubscriptionManageView.as_view(), name='manage'),
    path('checkout', SubscriptionCheckoutView.as_view(), name='checkout'),
    path('checkout/authentication', SubscriptionCheckoutAuthenticationView.as_view(), name='checkout_authentication'),
    path('checkout/success', SubscriptionCheckoutSuccessView.as_view(), name='checkout_success')
]