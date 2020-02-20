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
    subscription = models.OneToOneField(Subscription, on_delete=models.SET_NULL, null=True, blank=True)

    def move_to_free_plan(self):
        self.subscription.move_to_free_plan()
        self.user.groups.clear()
        free_hospitals_group, created = Group.objects.get(name='free_hospitals_group')
        self.user.groups.add(free_hospitals_group)
        self.user.groups.add(Group.objects.get(name='free_doctors_group'))

        doctors = Doctor.objects.filter(hospital=self)
        if doctors:
            for doctor in doctors:
                doctor.user.groups.clear()
                free_doctors_group, created = Group.objects.get(name='free_doctors_group')
                doctor.user.groups.add(free_doctors_group)

class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, related_name='doctors', null=True)

    @property
    def can_create_more_examinations(self):
        from examinations.models import Examination
        if Examination.objects.filter(created_by=self).count() >= 3 and not self.user.has_perm('common.can_exceed_max_examinations'):
            return False
        return True

@receiver(pre_save, sender=Hospital)
def pre_save_hospital_create_subscription(sender, instance, **kwargs):
    # add free Stripe plan
    free_plan = Plan.objects.filter(plan_type='free').first()
    customer = stripe.Customer.create(email=instance.user.email, name=instance.user.doctor.first_name + " " + instance.user.doctor.last_name)
    stripe_sub = stripe.Subscription.create(customer=customer.id, items=[{
        "plan": free_plan.stripe_plan_id
    }])
    sub = Subscription.objects.create(stripe_subscription_id=stripe_sub.id, stripe_customer_id=customer.id, plan=free_plan)
    instance.subscription = sub

@receiver(pre_save, sender=Doctor)
def pre_save_doctor_add_to_hospital(sender, instance, **kwargs):
    user_email_domain = instance.user.email.partition("@")[2]
    hospital = Hospital.objects.filter(email_domain=user_email_domain)
    if hospital:
        instance.hospital = hospital.first()

from common.utils import generate_doctor_groups_and_permissions, generate_hospital_groups_and_permissions

@receiver(post_save, sender=Doctor)
def post_save_doctor_create_and_add_groups(sender, instance, **kwargs):
    generate_doctor_groups_and_permissions()
    instance.user.groups.add(Group.objects.get(name='free_doctors_group'))
    if instance.hospital:
        if instance.hospital.user.groups.filter(name='pro_hospitals_group').exists():
            instance.user.groups.add(Group.objects.get(name='pro_doctors_group'))

@receiver(post_save, sender=Hospital)
def post_save_hospital_create_and_add_groups(sender, instance, **kwargs):
    generate_hospital_groups_and_permissions()
    instance.user.groups.add(Group.objects.get(name='free_hospitals_group'))

@receiver(post_save, sender=Hospital)
def post_save_hospital_add_doctors_to_hospital(sender, instance, **kwargs):
    users_matching_domain = CustomUser.objects.filter(email__contains=instance.email_domain)
    print('SIGNAL SENT')
    print(users_matching_domain)
    for user in users_matching_domain:
        user.doctor.hospital = instance
        user.doctor.save()

@receiver(pre_delete, sender=CustomUser)
def pre_delete_user_delete_doctor_hospital(sender, instance, **kwargs):
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
    

