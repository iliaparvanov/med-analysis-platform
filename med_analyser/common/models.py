from django.db import models
from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, Group
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
    email_domain = models.CharField(max_length=50, unique=True)

class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, related_name='doctors', null=True)
    subscription = models.OneToOneField(Subscription, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def can_create_more_examinations(self):
        from examinations.models import Examination
        if Examination.objects.filter(created_by=self).count() >= 3 and not self.user.has_perm('common.can_exceed_max_examinations'):
            return False
        return True

@receiver(pre_save, sender=Doctor)
def pre_save_create_subscription(sender, instance, **kwargs):
    # add free Stripe plan
    free_plan = Plan.objects.filter(plan_type='free').first()
    customer = stripe.Customer.create(email=instance.user.email, name=instance.first_name + " " + instance.last_name)
    stripe_sub = stripe.Subscription.create(customer=customer.id, items=[{
        "plan": free_plan.stripe_plan_id
    }])
    sub = Subscription.objects.create(stripe_subscription_id=stripe_sub.id, stripe_customer_id=customer.id, plan=free_plan)
    instance.subscription = sub

    # add hospital to doctor based on email domain
    hospital = Hospital.objects.filter(email_domain=instance.user.email.partition("@")[2])
    if hospital:
        instance.hospital = hospital.first()

from common.utils import generate_doctor_groups_and_permissions

@receiver(post_save, sender=Doctor)
def post_save_create_and_add_groups(sender, instance, **kwargs):
    generate_doctor_groups_and_permissions()
    free_doctors_group = Group.objects.get(name='free_doctors_group')
    instance.user.groups.add()

@receiver(pre_delete, sender=CustomUser)
def pre_delete_user_delete_doctor_hospital(sender, instance, **kwargs):
    # deleting a customer automatically cancels all active subscriptions
    instance.doctor.delete()
    if hasattr(instance, 'hospital'):
        instance.hospital.delete()

@receiver(pre_delete, sender=Doctor)
def pre_delete_doctor_delete_subscription(sender, instance, **kwargs):
    try:
        deleted_customer = stripe.Customer.delete(instance.subscription.stripe_customer_id)
    except: 
        pass

@receiver(pre_delete, sender=Hospital)
def pre_delete_hospital_delete_subscription(sender, instance, **kwargs):
    try:
        deleted_customer = stripe.Customer.delete(instance.subscription.stripe_customer_id)
    except: 
        pass
    

