from django.urls import path
from .views import ExaminationListView, ExaminationCreateView

urlpatterns = [
    path('', ExaminationListView.as_view(), name='examination_list'),
    path('new/', ExaminationCreateView.as_view(), name='examination_new')
]
