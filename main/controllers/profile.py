from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from main.entities.profile import UserProfile


@login_required(login_url='/login')
def profile(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.save()

        prof, created = UserProfile.objects.get_or_create(user=user)
        prof.phone_number = request.POST.get("phone_number", prof.phone_number)
        prof.address = request.POST.get("address", prof.address)
        prof.country = request.POST.get("country", prof.country)
        prof.state = request.POST.get("state", prof.state)
        prof.city = request.POST.get("city", prof.city)

        print('profile_image' in request.FILES)
        if 'profile_image' in request.FILES:
            prof.profile_image = request.FILES['profile_image']
        prof.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    context = {}
    return render(request, "profile/profile.html", context)

@login_required(login_url='/login')
def security(request):
    context = {}
    return render(request, "profile/security.html", context)

