from django.shortcuts import render

def about(request):
    context = {}
    return render(request, "settings/about.html", context)