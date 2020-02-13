from django.urls import path
from django.contrib.auth.decorators import login_required, permission_required
from .views import *

urlpatterns = [
    path('', ExaminationListView.as_view(), name='examination_list'),
    path('<uuid:pk>', ExaminationDetailView.as_view(), name='examination_detail'),
    path('new/', ExaminationCreateView.as_view(), name='examination_new'),
    path('<uuid:pk>/delete/', ExaminationDeleteView.as_view(), name='examination_delete'),
    path('<uuid:pk>/mark/no-finding', ExaminationMarkNoFindingView.as_view(), name='examination_mark_no_finding'),
    path('<uuid:pk>/mark/findings', ExaminationMarkFindingsView.as_view(), name='examination_mark_findings')
]
