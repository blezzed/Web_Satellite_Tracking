from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            print(allowed_roles)
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("You do not have permission to perform this action.")

        return wrapper_func

    return decorator

# def admin_only(view_func):
#     def wrapper_func(request, *args, **kwargs):
#         group = None
#         if request.user.groups.exists():
#             group = request.user.groups.all()[0].name
#
#         if group == "Student":
#             return redirect("/student/dashboard/")
#
#         if group == "Teacher":
#             return redirect("/teacher/dashboard/")
#
#         if group == "Parent":
#             return redirect("/parent/dashboard/")
#
#         if group == "Admin":
#             return view_func(request, *args, **kwargs)
#
#     return wrapper_func
