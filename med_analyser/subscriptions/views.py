from django.shortcuts import render, redirect
from django.views.generic import TemplateView, RedirectView
from django.views import View
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser, Group
from django.contrib import messages
from django.conf import settings
from subscriptions.models import Plan
from braces.views import *
from common.models import Doctor
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def get_desired_plan(request):
    plan_type = request.session.get('plan_type', 'nonexistant')
    return Plan.objects.filter(plan_type=plan_type).first()

def get_customer_id(user):
    return user.hospital.subscription.stripe_customer_id

def get_subscription(user):
    return  stripe.Subscription.retrieve(user.hospital.subscription.stripe_subscription_id)

def provision_goods(user, desired_plan):
    user.hospital.subscription.plan = desired_plan
    user.hospital.subscription.downgrade_at_period_end = False
    user.hospital.subscription.current_period_end = date.today() + relativedelta(months=+1)
    user.hospital.subscription.save()

    user.groups.add(Group.objects.get(name='pro_doctors_group'))
    user.groups.add(Group.objects.get(name='pro_hospitals_group'))

    doctors_in_hospital = Doctor.objects.filter(hospital=user.hospital)
    for doctor in doctors_in_hospital:
        doctor.user.groups.add(Group.objects.get(name='pro_doctors_group'))

class SubscriptionManageView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "common.is_hospital"
    raise_exception = True
    redirect_unauthenticated_users = True
    template_name = 'subscriptions/manage.html'

    def post(self, request, *args, **kwargs):
        plan_type = request.POST.get('plan_type')
        request.session['plan_type'] = plan_type
        return redirect(reverse('subscriptions:checkout'))

class SubscriptionCheckoutView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "common.is_hospital"
    raise_exception = True
    redirect_unauthenticated_users = True
    template_name = 'subscriptions/checkout.html'

    def post(self, request, *args, **kwargs):
        desired_plan = get_desired_plan(self.request)
        if desired_plan is None: return redirect(reverse('subscriptions:manage'))

        payment_method_id = request.POST['payment_method_id']
        customer_id = get_customer_id(self.request.user)
        stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
        customer = stripe.Customer.modify(customer_id,
            invoice_settings={
                'default_payment_method': payment_method_id,
            },
        )
        sub = get_subscription(self.request.user)
        stripe_sub = stripe.Subscription.modify(
            sub.id,
            cancel_at_period_end=False,
            items=[
                {
                    'id': sub['items']['data'][0].id,
                    'plan': desired_plan.stripe_plan_id,
                }
            ],
            payment_behavior='allow_incomplete',
            expand=['latest_invoice.payment_intent'],
        )
        status = stripe_sub.status
        if status == "active" and stripe_sub.latest_invoice.payment_intent.status == "succeeded":
            # payment succeeds, provision goods
            provision_goods(self.request.user, desired_plan)
            messages.add_message(request, messages.SUCCESS, 'Payment successful! You now have a ' + str(desired_plan))
            return redirect(reverse('subscriptions:checkout_success'))
        elif status == "past_due" and stripe_sub.latest_invoice.payment_intent.status == "requires_action":
            # requires further action, ie authentication
            messages.add_message(request, messages.ERROR,
            'This payment method requires extra authentication.')
            request.session['client_secret'] = stripe_sub.latest_invoice.payment_intent.client_secret
            return redirect(reverse('subscriptions:checkout_authentication'))
        else:
            # card error usually, ie. payment has failed
            messages.add_message(request, messages.ERROR,
            'Payment method invalid! Please fill in another payment method!')
            return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['first_name'] = self.request.user.doctor.first_name
        context['last_name'] = self.request.user.doctor.last_name    
        return context

class SubscriptionCheckoutAuthenticationView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "common.is_hospital"
    raise_exception = True
    redirect_unauthenticated_users = True
    template_name = 'subscriptions/checkout_authentication.html'

    def post(self, request, *args, **kwargs):
        try:
            desired_plan = get_desired_plan(self.request)
        except:
            return redirect(reverse('subcriptions:manage'))

        sub = get_subscription(self.request.user)
        if sub.status == 'active':
            provision_goods(self.request.user, desired_plan)
            messages.add_message(request, messages.SUCCESS, 'Payment successful! You now have a ' + str(desired_plan))
            return redirect(reverse('subscriptions:checkout_success'))
        else:
            return redirect(reverse('subscriptions:checkout'))


class SubscriptionCheckoutSuccessView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "common.is_hospital"
    raise_exception = True
    redirect_unauthenticated_users = True
    template_name = 'subscriptions/manage.html'

    def dispatch(self, *args, **kwargs):
        try:
            del request.session['plan_type']
        except:
            pass
        try:
            del request.session['client_secret']
        except:
            pass

        return super().dispatch(*args, **kwargs)

class SubscriptionCancelView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "common.is_hospital"
    raise_exception = True
    redirect_unauthenticated_users = True

    def post(self, request, *args, **kwargs):
        if self.request.user.hospital.subscription.downgrade_at_period_end:
            messages.add_message(self.request, messages.INFO,
            'Your subscription has already been canceled. You will not be charged at the end of your current billing period.')
            return redirect('common:home')

        self.request.user.hospital.subscription.downgrade_stripe_sub()

        self.request.user.hospital.subscription.downgrade_at_period_end = True
        self.request.user.hospital.subscription.save()

        messages.add_message(self.request, messages.INFO,
        'Your subscription has been canceled. You will not be charged at the end of your current billing period.')
        return redirect('common:home')