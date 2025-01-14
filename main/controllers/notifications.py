from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='/login')
def notifications(request):
    context = {"group": "satellite_notifications"}
    return render(request, "settings/notifications.html",{"webpush": context})