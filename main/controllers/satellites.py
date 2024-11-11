from django.shortcuts import render

def satellites(request):
    context = {}
    return render(request, "settings/satellites.html", context)