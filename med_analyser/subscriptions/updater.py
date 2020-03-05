from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.contrib.auth.models import Group

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def update_subscriptions(hospital_model, plan_model):
    hospitals_with_canceled_subs = hospital_model.objects.filter(subscription__downgrade_at_period_end=True)
    for hospital in hospitals_with_canceled_subs:
        if hospital.subscription.current_period_end <= datetime.today().date():
            # remove all pro privileges
            hospital.move_to_free_plan()

    hospitals_with_overdue_payments = hospital_model.objects.filter(subscription__current_period_end__lte=date.today() + relativedelta(days=-7))
    for hospital in hospitals_with_overdue_payments:
        sub_status = hospital.subcription.get_status
        if sub_status == 'past_due' or sub_status == 'canceled' or sub_status == 'unpaid':
            # move to free subscription
            hospital.subscription.downgrade_stripe_sub()
            hospital.move_to_free_plan()
        elif sub_status == 'active':
            hospital.subscription.current_period_end = date.today() + relativedelta(days=30)
            pass
    pass

def start(hospital_model, plan_model):
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_subscriptions, 'interval', [hospital_model, plan_model], minutes=30)
    scheduler.start()
