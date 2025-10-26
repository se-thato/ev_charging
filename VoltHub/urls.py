from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name=""),

    path('dashboard', views.dashboard, name="dashboard"),
    
    path('about_us', views.about_us, name="about_us"),

    path('contact_us', views.contact_us, name="contact_us"),

    path('book', views.booking, name="book"),

    #update your bookings
    path('update_booking/<int:pk>/', views.update_booking, name="update_booking"),

    #viewing a booking record
    path('view_booking/<int:pk>/', views.view_booking, name="view_booking"),

    # view a session record
    path('view_session/<int:pk>/', views.view_session, name="view_session"),


    #viewing a booking record
    path('delete_booking/<int:pk>/', views.delete_booking, name="delete_booking"),


    path('stations/', views.station_locator, name="stations"),
    path('stations/submit', views.submit_station, name="submit_station"),
    path('stations/verify', views.verify_stations, name="verify_stations"),

    #payment section
    path('payments', views.payment_methods, name="payments"),
    
    #billing section
    path('billing', views.billing, name="billing"),

    #profile section
    path('profile', views.profile, name="profile"),

    #posts section
    path('post_detail', views.post_detail, name="post_detail"),
    path('post_detail/<int:pk>/', views.post_detail, name='post_detail'),

    

]
