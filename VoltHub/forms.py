from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 

from django import forms
from django.forms.widgets import PasswordInput, TextInput

from charging_station.models import Booking, Profile


# Registration of a user 

class CreateUserForm(UserCreationForm):
    profile_picture = forms.ImageField(required=False, label="Profile Picture")

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'profile_picture']


# Login a user

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())


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
        fields = ['username', 'first_name', 'last_name', 'email', 'location']
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly'}),
            'first_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'last_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            'location': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
