from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RegistrationForm
# Create your views here.

def projects(request):
    return render(request, "Users/registration_form.html")

def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('projects')
    context = {'form' : form}
    return render(request, "Users/registration_form.html", context)