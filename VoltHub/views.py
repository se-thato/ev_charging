from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate

from django.contrib.auth.decorators import login_required

#Home page
def home(request):


    return render(request, 'VoltHub/index.html')


# Register View
def register(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('my-login')

    context = {'form': form}

    return render(request, 'VoltHub/register.html', context=context)



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

                return redirect('dashboard')

    context = {'form': form}

    return render(request, 'VoltHub/login.html', context=context)




# Dashboard view
@login_required(login_url='my-login')
def dashboard(request):
    stations = ChargingPoint.objects.all()
    sessions = ChargingSession.objects.filter(user=request.user)
    context = {
        'stations': stations,
        'sessions': section,
    }

    return render(request, 'VoltHub/dashboard.html', context)





# Logout user
def user_logout(request):

    auth.logout(request)

    return redirect('my-login')


#about user section

def about_us(request):
    return render(request, 'VoltHub/about_us.html')