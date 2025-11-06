from django.shortcuts import render, redirect
from .forms import BookingForm, UpdateBookingForm, ProfileForm, ChargingPointForm, CommentForm

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate

from django.contrib.auth.decorators import login_required, user_passes_test
from charging_station.models import ChargingPoint, ChargingSession, Booking, Profile, Comment, Post
from django.shortcuts import get_object_or_404

from django.conf import settings
import logging

from django.core.mail import send_mail
from django.http import HttpResponse

from django.core.mail import BadHeaderError
from django.contrib import messages
import logging

# Configure logging
logger = logging.getLogger(__name__)


#The main Home page
def home(request):
    #this will collect all the comment related to the VoltHub app/website
    comments = Comment.objects.filter(station__name='VoltHub').order_by('-created_at')
    return render(request, 'VoltHub/home.html', {'comments': comments})


# Dashboard view
@login_required(login_url='authentication:login')
def dashboard(request):
    try:
        stations = ChargingPoint.objects.filter(is_active=True)  # olny active stations
        sessions = ChargingSession.objects.filter(user=request.user).select_related('station')
        bookings = Booking.objects.filter(user=request.user).select_related('station')  # This will fetch user-specific bookings

        context = {
            'stations': stations,
            'sessions': sessions,
            'bookings': bookings,
        }
        return render(request, 'VoltHub/dashboard.html', context)

    except Exception as e:
        # Log the error (optional) and return an error message
        return HttpResponse(f"An error occurred: {str(e)}", status=500)




#about user section

def about_us(request):

    return render(request, 'VoltHub/about_us.html')


#contact us
def contact_us(request):
    # Handle contact form submission
    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        phone = request.POST.get('phone', '').strip()
        message_email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip() or f'Contact from {fullname}'
        message = request.POST.get('message', '').strip()

        # this part checks if all required fields are filled
        if not fullname or not message_email or not message:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'VoltHub/contact_us.html', {'error': 'Missing required fields.'})

        # Build email body
        body = (
            f"Name: {fullname}\n"
            f"Email: {message_email}\n"
            f"Phone: {phone}\n\n"
            f"Message:\n{message}"
        )

        #This part sends the email
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_RECEIVER_EMAIL], 
                fail_silently=False,
                #reply_to=[message_email] if message_email else None
            )
            #This part shows success message when the email is sent
            messages.success(request, "Your message was sent successfully! We'll get back to you soon.")
            return render(request, 'VoltHub/contact_us.html', {'success': True})
        
        #This part handles email sending errors
        except BadHeaderError:
            logger.error("Invalid header found when sending email.")
            messages.error(request, "Invalid header found.")

        except Exception as e:
            logger.exception("Error sending contact form email")
            messages.error(request, "Failed to send your message. Please try again later.")

    return render(request, 'VoltHub/contact_us.html')



@login_required(login_url='authentication:login')
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
@login_required(login_url='authentication:login')
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
@login_required(login_url='authentication:login')
def view_booking(request, pk):

    all_bookings = Booking.objects.get(id=pk)

    context = {'booking': all_bookings}

    return render(request, 'VoltHub/view_bookings.html', context=context)


# view a singular session record

def view_session(request, pk):

    sessions = ChargingSession.objects.get(id=pk)

    context = {'sessions': sessions}

    return render(request, 'VoltHub/view_session.html', context)


# delete booking record

@login_required(login_url='authentication:login')
def delete_booking(request, pk):

    booking = Booking.objects.get(id=pk)

    booking.delete()

    return redirect('dashboard')



@login_required(login_url='authentication:login')
def station_locator(request):
    # Only verified stations should be listed and mapped
    stations = ChargingPoint.objects.filter(is_verified=True, is_active=True)
    context = {'stations': stations}
    return render(request, 'VoltHub/charging_points.html', context)   



def payment_methods(request):
    payment_methods = ['Visa', 'MasterCard', 'PayPal', 'EFT', 'Cash']
    context = {'payment_methods': payment_methods}

    
    return render(request, 'VoltHub/payment_methods.html', context)



def billing(request):
    billing = ['Monthly', 'Weekly', 'Daily', 'Hourly']
    context = {'billing': billing}

    return render(request, 'VoltHub/billing.html', context)


@login_required(login_url='authentication:login')
def profile(request):
    try:
        user_profile = Profile.objects.get(username=request.user.username)
    except Profile.DoesNotExist:
        user_profile = Profile.objects.create(
            username=request.user.username,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            email=request.user.email
        )

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            profile_obj = form.save()
            # Sync selected Profile fields back to Djangos built in User model
            try:
                user = request.user
                # Only update if values differ to avoid unnecessary writes
                if hasattr(profile_obj, 'first_name'):
                    user.first_name = profile_obj.first_name or ''
                if hasattr(profile_obj, 'last_name'):
                    user.last_name = profile_obj.last_name or ''
                if hasattr(profile_obj, 'email') and profile_obj.email:
                    user.email = profile_obj.email
                user.save(update_fields=['first_name', 'last_name', 'email'])
            except Exception:
                # this will ensure we don't break user flow if sync fails
                pass
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=user_profile)

    context = {'form': form}
    return render(request, 'VoltHub/profile.html', context)


# Helper to restrict to admins
is_admin = user_passes_test(lambda u: u.is_superuser)


# Authenticated users submit a charging station; defaults to unverified
@login_required(login_url='authentication:login')
def submit_station(request):
    if request.method == 'POST':
        form = ChargingPointForm(request.POST)
        if form.is_valid():
            station = form.save(commit=False)
            station.owner = request.user
            station.created_by = request.user
            station.is_verified = False
            station.save()
            return redirect('stations')
    else:
        form = ChargingPointForm()
    return render(request, 'VoltHub/submit_station.html', {'form': form})


# listing pending stations and verify
@is_admin
def verify_stations(request):
    if request.method == 'POST':
        station_id = request.POST.get('station_id')
        action = request.POST.get('action')
        try:
            station = ChargingPoint.objects.get(id=station_id)
            if action == 'approve':
                station.is_verified = True
                station.updated_by = request.user
                station.save()
            elif action == 'reject':
                station.delete()
        except ChargingPoint.DoesNotExist:
            pass
        return redirect('verify_stations')

    pending = ChargingPoint.objects.filter(is_verified=False)
    return render(request, 'VoltHub/verify_stations.html', {'pending': pending})



def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post).order_by('-created_at')

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('post_detail', pk=post.pk)

    else:
        form = CommentForm()
        
        return render(request, 'VoltHub/post_details.html', {'post': post, 'comments': comments, 'form': form})
        
