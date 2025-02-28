from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 

from django import forms
from django.forms.widgets import PasswordInput, TextInput

from charging_station.models import Booking, Profile


# Registration of a user 

class CreateUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']


# Login a user

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())


#making your bookings
class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ['station', 'location', 'start_time', 'end_time', 'costs']


#updating your bookings
class UpdateBookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ['station', 'location', 'start_time', 'end_time','costs']


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