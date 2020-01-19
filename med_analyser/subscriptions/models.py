from django.db import models

# Create your models here.


class Plan(models.Model):
    
    PLAN_TYPES = [
        ('pro', 'Professional'),
        ('free', 'Free')
    ]
    stripe_plan_id = models.CharField(max_length=50)
    price = models.IntegerField(default=15)
    plan_type = models.CharField(max_length=4, choices=PLAN_TYPES, default='free')

class Subscription(models.Model):
    stripe_subscription_id = models.CharField(max_length=50)
    stripe_customer_id = models.CharField(max_length=50)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)