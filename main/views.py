from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from .decorators import unauthenticated_user, allowed_users
from .forms import CreateAdminUserForm


# Create your views here.
@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        identifier = request.POST.get('email')  # Identifier could be email or username
        password = request.POST.get('password')

        # Check if the identifier is an email or a username
        try:
            user = User.objects.filter(Q(username=identifier) | Q(email=identifier)).first()
            if user:
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect("/")
                else:
                    messages.error(request, 'Invalid credentials')
            else:
                messages.error(request, 'User not found')
        except Exception as e:
            messages.error(request, 'Something went wrong')

    context = {}
    return render(request, "authentication/login.html", context)

@unauthenticated_user
# @allowed_users(allowed_roles=['Admin'])
def register(request):

    form = CreateAdminUserForm()

    if request.method == "POST":
        form = CreateAdminUserForm(request.POST)

        if form.is_valid():
            print("Form is valid!")
            user = form.save()
            username = form.cleaned_data.get("username")

            group = Group.objects.get(name="scientist")
            user.groups.add(group)

            messages.success(request, f"Account was successfully created for {username}")
            return redirect("/login")
        else:
            print("Form is invalid:")
            print(form.errors)

    context = {'form': form}

    return render(request, "authentication/register.html", context)

def logoutUser(request):
    logout(request)
    return redirect('/login')
