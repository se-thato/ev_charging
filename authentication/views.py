from django.shortcuts import render, redirect
#jwt authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import auth
from .forms import UserRegisterForm, LoginForm
from charging_station.models import Profile
from django.contrib import messages as messages 



def activateEmail(request, user, to_email):
    messages.success(request, f'Dear <b>{user.username}</b>, please go to your email <b>{to_email}</b> inbox and click the verification link to verify your account!/<b>Note:</b> If you don\'t see the email, please check your spam folder.')


def register(request):
    form = UserRegisterForm()

    if request.method == "POST":
        form = UserRegisterForm(request.POST, request.FILES)  # Include request.FILES to handle file uploads
        if form.is_valid():
            user = form.save()
             
            messages.success(request, f"Account created for {user.username}!")

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
            
            Profile.objects.create(
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                profile_picture=form.cleaned_data.get('profile_picture')  # Save the uploaded profile picture
            )
 
            return redirect('authentication:login')

    context = {'form': form}

    return render(request, 'authentication/register.html', context=context)



# Login View
def my_login(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request,data=request.POST)
        if form.is_valid():
            
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            
            if user is not None:
                auth.login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard')

    context = {'form': form}

    return render(request, 'authentication/login.html', context=context)


def user_logout(request):
    auth.logout(request)

    return redirect('authentication:login')






class ProtectedView(APIView):
    """
    A protected view that requires JWT authentication.
    Returns a message and user-specific data for authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Return user-specific data
            user_data = {
                "username": request.user.username,
                "email": request.user.email,
            }
            return Response({"message": "This is protected", "user": user_data})
        except Exception as e:
            # Log the error (optional: integrate a logging framework)
            print(f"Error in ProtectedView: {e}")
        return Response({"error": "An unexpected error occurred."}, status=500)


