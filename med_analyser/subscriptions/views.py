from django.shortcuts import render, redirect
from django.views.generic import TemplateView, RedirectView
from django.views import View
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from subscriptions.models import Plan
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionManageView(LoginRequiredMixin, TemplateView):
    template_name = 'subscriptions/manage.html'

class SubscriptionCheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'subscriptions/checkout.html'

    def post(self, request, *args, **kwargs):
        plan_type = request.POST['plan_type']
        desired_plan = Plan.objects.filter(plan_type=plan_type).first()
        payment_method_id = request.POST['payment_method_id']
        customer_id = self.request.user.doctor.subscription.stripe_customer_id
        stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
        customer = stripe.Customer.modify(customer_id,
            invoice_settings={
                'default_payment_method': payment_method_id,
            },
        )
        sub = stripe.Subscription.retrieve(self.request.user.doctor.subscription.stripe_subscription_id)
        stripe_sub = stripe.Subscription.modify(
            sub.id,
            cancel_at_period_end=False,
            items=[
                {
                    'id': sub['items']['data'][0].id,
                    'plan': desired_plan.stripe_plan_id,
                }
            ],
            expand=['latest_invoice.payment_intent'],
        )
        if stripe_sub.status == "active" and stripe_sub.latest_invoice.payment_intent.status == "succeeded":
            # payment succeeds, provision goods
            request.user.doctor.subscription.plan = desired_plan
            request.user.doctor.subscription.save()
            messages.add_message(request, messages.SUCCESS, 'Payment successful!')
            return redirect(reverse('subscriptions:checkout_success'))
        elif stripe_sub.status == "incomplete" and stripe_sub.payment_intent.status == "requires_payment_method":
            messages.add_message(request, messages.ERROR, 'Payment method invalid! Please fill in another payment method!')
            context = {
                'plan_type': desired_plan.plan_type
            }
            return render(request, template_name, context)
        else:
            messages.add_message(request, messages.ERROR, 'Payment method invalid! Please fill in another payment method!')
            context = {
                
            }
            return render(request, template_name, context)
        
       

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not 'plan_type' in context.keys():
            desired_plan = Plan.objects.filter(plan_type=self.kwargs['plan_type']).first()
            context['plan_type'] = self.kwargs['plan_type']

        context['first_name'] = self.request.user.doctor.first_name
        context['last_name'] = self.request.user.doctor.last_name    

        return context

class SubscriptionCheckoutSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'subscriptions/checkout_success.html'

