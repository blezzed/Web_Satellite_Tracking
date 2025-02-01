from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='/login')
def about(request):
    context = {}
    return render(request, "settings/about.html", context)