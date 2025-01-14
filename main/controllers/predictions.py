from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='/login')
def predictions(request):
    context = {}
    return render(request, "predictions/index.html", context)
