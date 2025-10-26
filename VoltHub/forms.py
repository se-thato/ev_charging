#from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 

from django import forms
#from django.forms.widgets import PasswordInput, TextInput

from charging_station.models import Booking, Profile, ChargingPoint, Comment


# Registration of a user 
"""
class CreateUserForm(UserCreationForm):
    profile_picture = forms.ImageField(required=False, label="Profile Picture")

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'profile_picture']


# Login a user

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())
"""

#making your bookings
class BookingForm(forms.ModelForm):
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Booking Date'
    )


    class Meta:
        model = Booking
        fields = ['email', 'station', 'booking_date', 'duration', 'payment_method', 'status']


#updating your bookings
class UpdateBookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ['email', 'station', 'booking_date', 'duration', 'payment_method', 'status']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username', 'first_name', 'last_name', 'email', 'location', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly'}),
            'first_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'last_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            'location': forms.TextInput(attrs={'readonly': 'readonly'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
        }

# this form is for adding a new charging station
class ChargingPointForm(forms.ModelForm):
    class Meta:
        model = ChargingPoint
        fields = [
            'name',
            'location',
            'address',
            'latitude',
            'longitude',
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

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Write your comment here...',
        })
    )
    class Meta:
        model = Comment
        fields = ['content']