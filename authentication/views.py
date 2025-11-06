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

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings



def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uidb64_str = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uidb64_str)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for confirming your email address. You can now log in to your account.')
        return redirect('authentication:login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('VoltHub:home')


def activateEmail(request, user, to_email):
    mail_subject = "Activate your account"
    message = render_to_string("authentication/activate_account.html", {
        "user": user.username,
        "domain": get_current_site(request).domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": account_activation_token.make_token(user),
        "protocol": "https" if request.is_secure() else "http",
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user.username}, please go to your email {to_email} inbox and click the verification link to verify your account!Note: If you don\'t see the email, please check your spam folder.')
    else:
        messages.error(request, f'Dear {user.username}, there was an error sending the verification email. Please try again later.')



def register(request):
    form = UserRegisterForm()

    if request.method == "POST":
        form = UserRegisterForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            email = form.cleaned_data.get('email') #this is to get the email from the form

            # Check if Profile with same email exists
            if Profile.objects.filter(email=email).exists():
                messages.error(request, "A profile with this email already exists.")
                return redirect('authentication:register')
            
            #This part creates the user
            user = form.save(commit=False)  # Don't save yet
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()  # Now we will save the user
            activateEmail(request, user, form.cleaned_data.get('email'))  # Send activation email
            messages.success(request, f"Activation email sent to {form.cleaned_data.get('email')}.")

            # Create Profile only after the user has been successfully created
            Profile.objects.get_or_create(
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                profile_picture=form.cleaned_data.get('profile_picture')
            )

            messages.success(request, f"Account created for {user.username}!")

            #sending a welcome email
            send_mail(
                'Welcome to VoltHub!',
                'Thank you for registering at VoltHub. We are excited to have you on board!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[form.cleaned_data['email']],
                fail_silently=False,
            )
            

            return redirect('authentication:login')
        
        else:
            # Display all errors (including duplicate email)
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = UserRegisterForm()

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


