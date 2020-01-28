from django.db import models
from django.conf import settings
from datetime import datetime
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY



class Plan(models.Model):
    
    PLAN_TYPES = [
        ('pro', 'Professional'),
        ('free', 'Free')
    ]
    stripe_plan_id = models.CharField(max_length=50)
    price = models.IntegerField(default=15)
    plan_type = models.CharField(max_length=4, choices=PLAN_TYPES, default='free')

    def __str__(self):
        return self.plan_type + " plan"

class Subscription(models.Model):
    stripe_subscription_id = models.CharField(max_length=50, null=True)
    stripe_customer_id = models.CharField(max_length=50, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)

    def is_active(self):
        Subscription = stripe.Subscription.retrieve(self.stripe.subscription_id)
        return datetime.fromtimestamp(subscription.active)

    @property
    def get_next_billing_date(self):
        subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
        return datetime.fromtimestamp(subscription.current_period_end)
