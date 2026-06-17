from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import ChargingSession
from .tasks import send_charging_complete_email
from .tasks import generate_invoice_and_email

from django.conf import settings
from .models import Profile, Booking, Notification




@receiver(post_save, sender=ChargingSession)
def notify_charging_session_complete(sender, instance, created, **kwargs):
    if not created and instance.status.lower() == "completed":
        send_charging_complete_email.delay(instance.id)


# This function uses pre_save and post_save signals to trigger the invoice generation task
# The pre_save checks if the end_time is being set on an existing record
@receiver(pre_save, sender=ChargingSession)
def charging_session_pre_save(sender, instance, **kwargs):
    """
    This pre_save signal checks if the ChargingSession is being updated to have an end_time.
    If so, it sets a flag on the instance to generate an invoice after save.
    This avoids doing Db queries in post_save and ensures the task is only triggered when needed.
    """
    if not instance.pk:
        # new instance being created
        if instance.end_time:
            instance._generate_invoice = True
        return

    try:
        old = ChargingSession.objects.get(pk=instance.pk)
    except ChargingSession.DoesNotExist:
        return

    # If previously had no end_time and now has an end_time , mark to generate invoice
    if old.end_time is None and instance.end_time is not None:
        instance._generate_invoice = True


@receiver(post_save, sender=ChargingSession)
def charging_session_post_save(sender, instance, created, **kwargs):
    """
    After save, if flagged by pre_save, dispatch the Celery task.
    """
    if getattr(instance, "_generate_invoice", False) or (created and instance.end_time):
        # Clean flag (not strictly necessary but tidy)
        if hasattr(instance, "_generate_invoice"):
            del instance._generate_invoice
        # Fire the background job
        generate_invoice_and_email.delay(instance.pk)



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    This signal fires after a new User is created.
    Automatically creates a linked Profile so every
    user always has a profile without us manually doing it.
    """
    if created:
        Profile.objects.create(user=instance)


#This signal fires after any User is updated and keeps the Profile in sync when User details change.
# The hasattr check prevents crashing if a user somehow has no profile yet.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

#This signal fires after a new Booking is created and sends a notification to the user confirming their booking.
@receiver(post_save, sender=Booking)
def create_booking_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            message=f"Booking confirmed for {instance.station} "
                    f"from {instance.start_time} to {instance.end_time}."
        )