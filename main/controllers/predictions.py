from django.shortcuts import render


def predictions(request):
    context = {}
    return render(request, "predictions/index.html", context)
