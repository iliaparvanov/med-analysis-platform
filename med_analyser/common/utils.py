from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType 
from .models import Doctor

def generate_doctor_groups_and_permissions():
    ct = ContentType.objects.get_for_model(Doctor)

    pro_doctors_group, created = Group.objects.get_or_create(name ='pro_doctors_group')
    free_doctors_group, created = Group.objects.get_or_create(name ='free_doctors_group') 

    is_doctor_perm, created = Permission.objects.get_or_create(codename='is_doctor', name='The user is a doctor and so can access all doctor-specific functionality', content_type=ct)
    max_examinations_perm, created = Permission.objects.get_or_create(codename='can_exceed_max_examinations', name='Can create more than the standard maximum for examinations', content_type=ct)

    free_doctors_group.permissions.add(is_doctor_perm)
    pro_doctors_group.permissions.add(is_doctor_perm)
    pro_doctors_group.permissions.add(max_examinations_perm)
