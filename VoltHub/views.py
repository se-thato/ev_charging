from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm, BookingForm, UpdateBookingForm

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate

from django.contrib.auth.decorators import login_required
from charging_station.models import ChargingPoint, ChargingSession, Booking

from django.core.mail import send_mail
from django.http import HttpResponse

#Home page
def home(request):


    return render(request, 'VoltHub/home.html')


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
    bookings = Booking.objects.all()
    context = {
        'stations': stations,
        'sessions': sessions,
        'bookings': bookings,
    }

    return render(request, 'VoltHub/dashboard.html', context)





# Logout user
def user_logout(request):

    auth.logout(request)

    return redirect('my-login')


#about user section

def about_us(request):

    return render(request, 'VoltHub/about_us.html')


#contact us

def contact_us(request):
    if request.method == 'POST': 
        name = request.POST.get('name')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Process or send the email
        send_mail(
            f'Contact Us Message from {name}',
            f'Contact Number: {contact_number}\nMessage:\n{message}',
            email,
            ['thatoselepe53@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse("Thank you for your message!")
    
    return render(request, 'VoltHub/contact_us.html')


@login_required(login_url='my-login')
def booking(request):

    form = BookingForm()

    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('dashboard')

    context = {'form': form}


    return render(request, 'VoltHub/booking.html', context=context)


# update your bookings

@login_required(login_url='my-login')
def update_booking(request, pk):

    booking = Booking.objects.get(id=pk)

    form = UpdateBookingForm(instance=booking)

    if request.method == 'POST':
        form =UpdateBookingForm(request.POST, instance=booking)

        if form.is_valid():

            form.save()

            return redirect("dashboard")

    context = {'form': form}


    return render(request, 'VoltHub/update_booking.html', context=context)



# view a singular booking record

@login_required(login_url='my-login')
def view_booking(request, pk):

    all_bookings = Booking.objects.get(id=pk)

    context = {'booking': all_bookings}

    return render(request, 'VoltHub/view_bookings.html', context=context)


# delete booking record

@login_required(login_url='my-login')
def delete_booking(request, pk): 

    booking = Booking.objects.get(id=pk)

    booking.delete()

    return redirect('dashboard')
