from django.urls import path
from django.contrib.auth.decorators import login_required, permission_required
from .views import ExaminationListView, ExaminationCreateView, ExaminationDetailView, ExaminationDeleteView

urlpatterns = [
    path('', ExaminationListView.as_view(), name='examination_list'),
    path('<uuid:pk>', ExaminationDetailView.as_view(), name='examination_detail'),
    path('new/', permission_required('can_exceed_max_examinations')(ExaminationCreateView.as_view()), name='examination_new'),
    path('<uuid:pk>/delete/', ExaminationDeleteView.as_view(), name='examination_delete'),
]
