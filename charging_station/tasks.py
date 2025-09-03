from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta



#this task sends an order confirmation email to the user
#it takes the user's email, order id, delivery type, and address as parameters
@shared_task
def send_order_confirmation_email(user_email, order_id, delivery_type, address=None):
    if delivery_type == 'delivery':
        estimated_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        message = (
            f"Thank you for your purchase!\n\n"
            f"Your order #{order_id} is being prepared and will be delivered to {address}.\n"
            f"Estimated delivery date: {estimated_date}."
        )
    else:
        estimated_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        message = (
            f"Thank you for your purchase!\n\n"
            f"Your order #{order_id} is being prepared.\n"
            f"You can pick it up on: {estimated_date}."
        )

    send_mail(
        subject="Order Confirmation",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )

# Task to send order status update emails
@shared_task
def send_order_status_update_email(user_email, order_id, new_status):
    subject = f"Order #{order_id} Status Update"
    message = f"Dear customer,\n\nYour order #{order_id} has been updated to '{new_status}'.\n\nThank you for shopping with us hope to see you again soon!"

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    
    send_mail(
        subject="Status Update for Your Order",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )