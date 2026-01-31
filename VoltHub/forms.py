#from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 

from django import forms
#from django.forms.widgets import PasswordInput, TextInput

from charging_station.models import Booking, Profile, ChargingPoint, Comment


#making your bookings
class BookingForm(forms.ModelForm):
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Booking Date'
    )

    # Optional start time so users can pick an exact datetime.
    # `datetime-local` produces a naive datetime string in the user's local
    # timezone; we convert it to an aware datetime in the view.
    start_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label='Start Time (optional)'
    )

    class Meta:
        model = Booking
        # Do NOT expose `status` to users; default remains 'pending' at the model level.
        fields = ['email', 'station', 'booking_date', 'start_time', 'duration', 'payment_method']


#updating your bookings
class UpdateBookingForm(forms.ModelForm):

    start_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label='Start Time (optional)'
    )

    class Meta:
        model = Booking
        # Do NOT expose `status` to users; only backend/admin should change it.
        fields = ['email', 'station', 'booking_date', 'start_time', 'duration', 'payment_method']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username', 'first_name', 'last_name', 'email', 'location', 'profile_picture']
        widgets = {
            
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

# this form is for adding a new charging station
class ChargingPointForm(forms.ModelForm):
    class Meta:
        model = ChargingPoint
        fields = [
            'name',
            'location',
            'address',
            'capicity',
            'available_slots',
            'availability',
            'price_per_hour',
            'off_peak_start',
            'off_peak_end',
            'is_active',
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'capicity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'available_slots': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'availability': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'price_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'off_peak_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'off_peak_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# form for adding comments
class CommentForm(forms.ModelForm):
    comment_text = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Write your comment here...',
        })
    )
    class Meta:
        model = Comment
        fields = ['comment_text']