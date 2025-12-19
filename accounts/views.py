from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView

from .forms import RegistrationForm, UserUpdateForm


# ---------------------------
# LANDING PAGE
# ---------------------------
def index(request):
    return render(request, 'core/index.html')


# ---------------------------
# REGISTRATION
# ---------------------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect('quizzes:dashboard')   # If logged in → go to dashboard

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to AI Quiz Hub.")
            return redirect('quizzes:dashboard')
        else:
            # If the form is NOT valid, the code jumps here.
            # You must pass the form back to the template to display errors.
            print("Form validation failed. Errors:", form.errors) # DEBUG LINE
            # If you see this printout, check form.errors for the reason
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# ---------------------------
# LOGIN VIEW (Custom Redirection)
# ---------------------------
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True    # Prevent logged users from seeing login page

    # override success URL
    def get_success_url(self):
        return redirect('quizzes:dashboard').url


# ---------------------------
# PROFILE PAGE (User model only — no UserProfile)
# ---------------------------
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated")
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'u_form': form})



# ---------------------------
# LOGOUT
# ---------------------------
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('accounts:login')
