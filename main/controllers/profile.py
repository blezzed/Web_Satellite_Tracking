from random import randint

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
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
    user_profile = get_object_or_404(UserProfile, user=request.user)  # Get the logged-in user's profile
    context = {
        'phone_number': user_profile.phone_number,  # Pass phone_number to the template
        'phone_verified': True  # Example: Add a placeholder for verification status
    }
    return render(request, "profile/security.html", context)


@login_required(login_url='/login')
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Validate passwords
        if new_password != confirm_password:
            messages.error(request, "New passwords don't match.")
            return redirect("security")

        # Check current password and update
        user = request.user
        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()

            # Ensures the session remains valid after the password change
            update_session_auth_hash(request, user)

            messages.success(request, "Password updated successfully!")
            return redirect("security")
        else:
            messages.error(request, "Current password is incorrect.")
            return redirect("security")

    return redirect("security")

@login_required(login_url='/login')
def update_phone_number(request):
    if request.method == "POST":
        user_profile = get_object_or_404(UserProfile, user=request.user)
        new_phone_number = request.POST.get("phone_number")
        verification_code = request.POST.get("verification_code")

        # Verify the phone number using a placeholder verification mechanism
        if verification_code:
            # Assume successful verification for demonstration
            user_profile.phone_number = new_phone_number
            messages.success(request, "Phone number updated successfully and verified!")
        else:
            # Send verification code to the user (mocked)
            generated_code = randint(100000, 999999)
            print(f"Verification code sent to {new_phone_number}: {generated_code}")  # Replace with actual SMS service
            messages.info(request, "Verification code sent to your new phone number, please verify.")

        user_profile.save()
        return redirect("security")
    return redirect("security")

@login_required
def deactivate_user(request):
    """Toggle the user's active status to deactivate their account."""
    if request.method == "POST":
        user = request.user
        user.is_active = False  # Set user inactive
        user.save()  # Save changes to the database
        return JsonResponse({"message": "Account deactivated successfully.", "is_active": user.is_active}, status=200)
    return JsonResponse({"error": "Invalid request method."}, status=400)

@login_required
def delete_user_account(request):
    """Deletes the currently logged-in user's account permanently."""
    if request.method == "POST":
        user = request.user
        user.delete()  # Permanently delete the user from the database
        return JsonResponse({"message": "Your account has been deleted permanently."}, status=200)
    return JsonResponse({"error": "Invalid request method."}, status=400)
