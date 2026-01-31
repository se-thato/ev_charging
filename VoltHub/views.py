from django.shortcuts import render, redirect
from .forms import BookingForm, UpdateBookingForm, ProfileForm, ChargingPointForm, CommentForm

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required, user_passes_test
from charging_station.models import ChargingPoint, ChargingSession, Booking, Profile, Comment, Post
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import redirect_to_login

from django.conf import settings
import logging

from django.core.mail import send_mail
from django.http import HttpResponse

from django.core.mail import BadHeaderError
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import F
import logging

# Configure logging
logger = logging.getLogger(__name__)


#The main Home page
def home(request):
    #this will collect all the comment related to the VoltHub app/website
    comments = Comment.objects.filter(station__name='VoltHub').order_by('-created_at')
    # Ensure there is a Post to host general comments; create a default one if none exists
    post_to_comment = Post.objects.order_by('-created_at').first()
    if not post_to_comment:
        User = get_user_model()
        author = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if author:
            post_to_comment = Post.objects.create(
                title='Community Feedback',
                content='Share your thoughts about VoltHub.',
                author=author,
            )
    return render(request, 'VoltHub/home.html', {'comments': comments, 'post_to_comment': post_to_comment})


# # Dashboard view
# @login_required(login_url='authentication:login')
# def dashboard(request):
#     try:
#         stations = ChargingPoint.objects.filter(is_active=True)  # olny active stations
#         sessions = ChargingSession.objects.filter(user=request.user).select_related('station')
#         bookings = Booking.objects.filter(user=request.user).select_related('station')  # This will fetch user specific bookings

#         context = {
#             'stations': stations,
#             'sessions': sessions,
#             'bookings': bookings,
#         }
#         return render(request, 'VoltHub/dashboard.html', context)

#     except Exception as e:
#         # 
#         return HttpResponse(f"An error occurred: {str(e)}", status=500)




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
            # attach user and persist booking
            booking = form.save(commit=False)
            if not booking.user_id:
                booking.user = request.user
            try:
                booking.created_by = request.user
            except Exception:
                pass
            try:
                booking.updated_by = request.user
            except Exception:
                pass

            # If the form provided an explicit start_time, prefer it. The
            # `datetime-local` widget yields a naive datetime in local time, so
            # make it timezone-aware before saving. Otherwise fall back to the
            # booking_date at midnight or now as before.
            from datetime import datetime, time
            from django.utils import timezone as dj_timezone

            provided_start = form.cleaned_data.get('start_time')
            if provided_start:
                # make aware if naive
                if dj_timezone.is_naive(provided_start):
                    provided_start = dj_timezone.make_aware(provided_start)
                booking.start_time = provided_start
            else:
                if not getattr(booking, 'start_time', None):
                    if booking.booking_date:
                        naive_dt = datetime.combine(booking.booking_date, time.min)
                        booking.start_time = dj_timezone.make_aware(naive_dt)
                    else:
                        # fallback to immediate start if booking_date missing
                        booking.start_time = dj_timezone.now()

            # If duration provided, compute end_time automatically
            if booking.duration and booking.start_time and not booking.end_time:
                booking.end_time = booking.start_time + booking.duration

            booking.save()

            # Send confirmation email to the user via Brevo 
            to_email = booking.email or getattr(request.user, 'email', None)
            if to_email:
                subject = "Your EV Charging Booking Confirmation"

                from django.utils import timezone as dj_timezone

                start_display = "N/A"
                end_display = "N/A"
                if booking.start_time:
                    start_display = dj_timezone.localtime(booking.start_time).strftime("%Y-%m-%d %H:%M")
                if booking.end_time:
                    end_display = dj_timezone.localtime(booking.end_time).strftime("%Y-%m-%d %H:%M")

                plain_body = (
                    f"Hello {request.user.first_name or request.user.username},\n\n"
                    f"Your booking at {booking.station.name} on {booking.booking_date} is received.\n"
                    f"Start: {start_display}\n"
                    f"End: {end_display}\n"
                    f"Status: {booking.status}\n\n"
                    f"Thank you for using VoltHub."
                )
                html_body = (
                    f"<p>Hello {request.user.first_name or request.user.username},</p>"
                    f"<p>Your booking at <strong>{booking.station.name}</strong> on <strong>{booking.booking_date}</strong> is confirmed.</p>"
                    f"<p><strong>Start:</strong> {start_display}</p>"
                    f"<p><strong>End:</strong> {end_display}</p>"
                    f"<p>Status: <strong>{booking.status}</strong></p>"
                    f"<p>Thank you for using <strong>VoltHub</strong>.</p>"
                )
                try:
                    send_mail(
                        subject=subject,
                        message=plain_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[to_email],
                        html_message=html_body,
                        fail_silently=True,
                    )
                except Exception:
                    # Do not block user flow on email issues
                    pass

            messages.success(request, "Booking created successfully.")
            return redirect('user_dashboard')

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
            # Save but allow us to compute dependent datetimes
            updated = form.save(commit=False)

            from datetime import datetime, time
            from django.utils import timezone as dj_timezone

            provided_start = form.cleaned_data.get('start_time')
            if provided_start:
                if dj_timezone.is_naive(provided_start):
                    provided_start = dj_timezone.make_aware(provided_start)
                updated.start_time = provided_start
            else:
                if not getattr(updated, 'start_time', None):
                    if updated.booking_date:
                        naive_dt = datetime.combine(updated.booking_date, time.min)
                        updated.start_time = dj_timezone.make_aware(naive_dt)
                    else:
                        updated.start_time = dj_timezone.now()

            if updated.duration and updated.start_time:
                updated.end_time = updated.start_time + updated.duration

            # Ensure users cannot change booking status via the update form.
            updated.status = booking.status

            updated.save()

            return redirect('user_dashboard')

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

    return redirect('user_dashboard')



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
    # Show a post detail page but use station based comments bound to the "VoltHub" station
    post = get_object_or_404(Post, pk=pk)

    station, _ = ChargingPoint.objects.get_or_create(
        name='VoltHub',
        defaults={
            'capicity': 0,
            'available_slots': 0,
        
        }
    )

    comments = Comment.objects.filter(station=station).order_by('-created_at')

    if request.method == "POST":
        # Require authentication for comment submission
        if not request.user.is_authenticated:
            return redirect_to_login(next=request.get_full_path())
        # Accept both potential field names to be tolerant of existing templates
        text = (request.POST.get('comment_text') or request.POST.get('content') or '').strip()
        if not text:
            messages.error(request, 'Please enter a comment before submitting.')
        else:
            try:
                existing = Comment.objects.filter(user=request.user, station=station).first()
                if existing:
                    # Bypass model.save() duplicate check by using QuerySet.update
                    Comment.objects.filter(pk=existing.pk).update(comment_text=text)
                    messages.success(request, 'Your comment has been updated.')
                else:
                    Comment.objects.create(user=request.user, station=station, comment_text=text)
                    messages.success(request, 'Your comment has been posted.')
                return redirect('post_detail', pk=post.pk)
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, 'Failed to submit your comment. Please try again.')

    # Render the page; template should show existing comments and a textarea to submit
    return render(request, 'VoltHub/post_details.html', {
        'post': post,
        'comments': comments,
    })


@login_required(login_url='authentication:login')
def comment_upvote(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, pk=comment_id)
        Comment.objects.filter(pk=comment.pk).update(upvotes=F('upvotes') + 1)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='authentication:login')
def comment_downvote(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, pk=comment_id)
        Comment.objects.filter(pk=comment.pk).update(downvotes=F('downvotes') + 1)
    return redirect(request.META.get('HTTP_REFERER', '/'))
        
