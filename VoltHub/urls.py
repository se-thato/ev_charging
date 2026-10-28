from django.urls import path

#from charging_station.views import StationOwnerDashboardView
from . import views


urlpatterns = [
    path('', views.home, name=""),

    path('dashboard', views.dashboard, name="dashboard"),

     path('owner_dashboard',views.owner_dashboard,name='owner_dashboard'),
    
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
    path('stations/<int:pk>/', views.station_detail, name="station_detail"),
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
    
    # comment reactions
    path('comments/<int:comment_id>/upvote/', views.comment_upvote, name='comment_upvote'),
    path('comments/<int:comment_id>/downvote/', views.comment_downvote, name='comment_downvote'),

    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('vehicle/update/', views.update_vehicle, name='update_vehicle'),
    path('report-issue/', views.report_issue, name='report_issue'),


    #smartcar
    path('smartcar/connect/',  views.smartcar_connect,  name='smartcar_connect'),
    path('smartcar/callback/', views.smartcar_callback, name='smartcar_callback'),
    path('smartcar/status/',   views.vehicle_status,    name='vehicle_status'),
    
    ]
