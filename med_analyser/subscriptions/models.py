from django.db import models
from django.conf import settings
from datetime import datetime, date
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
    current_period_end = models.DateField(default=date(2040, 1, 1))
    downgrade_at_period_end = models.BooleanField(default=False) 

    def is_active(self):
        Subscription = stripe.Subscription.retrieve(self.stripe.subscription_id)
        return datetime.fromtimestamp(subscription.active)

    def move_to_free_plan(self):
        self.plan = Plan.objects.filter(plan_type='free').first()
        self.downgrade_at_period_end = False
        self.current_period_end = date(2040, 1, 1)
        self.save()

    def downgrade_stripe_sub(self):
        stripe_sub = stripe.Subscription.retrieve(self.stripe_subscription_id)
        stripe.Subscription.modify(
                stripe_sub.id,
                cancel_at_period_end=False,
                items=[{
                    'id': stripe_sub['items']['data'][0].id,
                    'plan': Plan.objects.filter(plan_type='free').first().stripe_plan_id,
            }]
        )

    @property
    def get_next_billing_date(self):
        subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
        return datetime.fromtimestamp(subscription.current_period_end)

    @property
    def get_status(self):
        subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
        return subscription.status
