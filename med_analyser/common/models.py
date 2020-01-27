from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings
from subscriptions.models import Subscription, Plan
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class CustomUser(AbstractUser):
    pass

class Hospital(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField()

class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, related_name='doctors', null=True)
    subscription = models.OneToOneField(Subscription, on_delete=models.SET_NULL, null=True, blank=True)

@receiver(pre_save, sender=Doctor)
def post_save_create_subscription(sender, instance, **kwargs):
    free_plan = Plan.objects.filter(plan_type='free').first()
    customer = stripe.Customer.create(email=instance.user.email)
    stripe_sub = stripe.Subscription.create(customer=customer.id, items=[{
        "plan": free_plan.stripe_plan_id
    }])
    sub = Subscription.objects.create(stripe_subscription_id=stripe_sub.id, stripe_customer_id=customer.id, plan=free_plan)
    instance.subscription = sub
    instance.save()

