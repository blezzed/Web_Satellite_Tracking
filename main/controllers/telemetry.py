from django.shortcuts import render


def telemetry(request):
    context = {}
    return render(request, "telemetry/index.html", context)
