from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name=""),

    path('register', views.register, name="register"),

    path('my-login', views.my_login, name="my-login"),

    path('dashboard', views.dashboard, name="dashboard"),

    path('logout-user', views.user_logout, name="logout-user"),

    path('about_us', views.about_us, name="about_us"),

    
    path('contact_us', views.contact_us, name="contact_us"),

    path('book', views.booking, name="book"),

    #update your bookings

    path('update_booking/<int:pk>/', views.update_booking, name="update_booking"),

    #viewing a booking record

    path('view_booking/<int:pk>/', views.view_booking, name="view_booking"),


    #viewing a booking record

    path('delete_booking/<int:pk>/', views.delete_booking, name="delete_booking"),


    path('stations/', views.station_locator, name="station_locator"),

]
