from django.shortcuts import render, redirect
from django.views.generic import TemplateView, RedirectView
from django.views import View
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from subscriptions.models import Plan
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def get_desired_plan(request):
    plan_type = request.session.get('plan_type', 'nonexistant')
    return Plan.objects.filter(plan_type=plan_type).first()


class SubscriptionManageView(LoginRequiredMixin, TemplateView):
    template_name = 'subscriptions/manage.html'

    def post(self, request, *args, **kwargs):
        plan_type = request.POST.get('plan_type')
        request.session['plan_type'] = plan_type
        return redirect(reverse('subscriptions:checkout'))


class SubscriptionCheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'subscriptions/checkout.html'

    def post(self, request, *args, **kwargs):
        desired_plan = get_desired_plan(self.request)
        if desired_plan is None:
            return redirect(reverse('subscriptions:manage'))

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
            payment_behavior='allow_incomplete',
            expand=['latest_invoice.payment_intent'],
        )
        print(stripe_sub)
        if stripe_sub.status == "active" and stripe_sub.latest_invoice.payment_intent.status == "succeeded":
            # payment succeeds, provision goods
            request.user.doctor.subscription.plan = desired_plan
            request.user.doctor.subscription.save()
            messages.add_message(request, messages.SUCCESS, 'Payment successful!')
            return redirect(reverse('subscriptions:checkout_success'))
        elif stripe_sub.status == "past_due" and stripe_sub.latest_invoice.payment_intent.status == "requires_action":
            # requires further action, ie authentication
            messages.add_message(request, messages.ERROR, 'This payment method requires extra authentication.')
            request.session['client_secret'] = stripe_sub.latest_invoice.payment_intent.client_secret
            return redirect(reverse('subscriptions:checkout_authentication'))
        else:
            # card error usually, ie. payment has failed
            messages.add_message(request, messages.ERROR, 'Payment method invalid! Please fill in another payment method!')
            return render(request, self.template_name)
        
       

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['first_name'] = self.request.user.doctor.first_name
        context['last_name'] = self.request.user.doctor.last_name    

        return context

class SubscriptionCheckoutAuthenticationView(LoginRequiredMixin, TemplateView):
    template_name = 'subscriptions/checkout_authentication.html'

    def post(self, request, *args, **kwargs):
        try:
            desired_plan = get_desired_plan(self.request)
        except:
            return redirect(reverse('subcriptions:manage'))

        sub = stripe.Subscription.retrieve(self.request.user.doctor.subscription.stripe_subscription_id)
        if sub.status == 'active':
            request.user.doctor.subscription.plan = desired_plan
            request.user.doctor.subscription.save()
            return redirect(reverse('subscriptions:checkout_success'))
        else:
            return redirect(reverse('subscriptions:checkout'))
        



class SubscriptionCheckoutSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'subscriptions/checkout_success.html'

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

