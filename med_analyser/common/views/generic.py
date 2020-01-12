from django.shortcuts import redirect, render
from django.views.generic import TemplateView

class HomePageView(TemplateView):
    template_name = 'home.html'

class SignUpView(TemplateView):
    template_name = 'account/signup.html'

class ProfileView(TemplateView):
    template_name = "profile.html"
'''
def home(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('teachers:quiz_change_list')
        else:
            return redirect('students:quiz_list')
    return render(request, 'classroom/home.html')
'''