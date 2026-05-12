from django.shortcuts import render, redirect

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required


# =========================================================
# LOGIN VIEW
# =========================================================

def login_view(request):

    error_message = ""

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("chatbot")

        else:

            error_message = (
                "Invalid username or password"
            )

    return render(
        request,
        "login.html",
        {
            "error_message": error_message
        }
    )


# =========================================================
# LOGOUT VIEW
# =========================================================

@login_required
def logout_view(request):

    logout(request)

    return redirect("login")