from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import ChargingSession
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage



@shared_task
def send_charging_complete_email(session_id):
    try:
        session = ChargingSession.objects.get(id=session_id)
        user = session.user

        subject = "Charging Session Complete"
        message = (
            f"Hello {user.first_name},\n\n"
            f"Your charging session at {session.station.name} has been completed.\n"
            f"Session details:\n"
            f"- Duration: {session.duration} minutes\n"
            f"- Energy Delivered: {session.energy_delivered} kWh\n"
            f"- Cost: {session.cost} {session.currency}\n\n"
            "Thank you for using our service!"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return f"Email sent to {user.email} for session {session.id}"

    except ChargingSession.DoesNotExist:
        return f"Session {session_id} not found"



# Task to generate invoice PDF and email it to the user
@shared_task(bind=True)
def generate_invoice_and_email(self, session_id):
    # imported inside the function to avoild circular imports
    from .models import ChargingSession

    try:
        session = ChargingSession.objects.select_related('user', 'station').get(pk=session_id)
    except ChargingSession.DoesNotExist:
        return f"Session {session_id} not found"

    user = session.user
    user_email = getattr(user, 'email', None)
    if not user_email:
        return f"Session {session_id} has no user email"

    # Creating PDF in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "VoltHub Charging Receipt")
    y -= 30

    p.setFont("Helvetica", 11)
    def line(text):
        nonlocal y
        p.drawString(50, y, text)
        y -= 18

    # Convenience to get user name safely
    try:
        full_name = user.get_full_name() if callable(getattr(user, "get_full_name", None)) else str(user)
    except Exception:
        full_name = str(user)

    line(f"Invoice ID: INV-{session.id:06d}")
    line(f"User: {full_name}")
    line(f"Email: {user_email}")
    line(f"Station: {session.station.name}")
    line(f"Start: {session.start_time.strftime('%Y-%m-%d %H:%M') if session.start_time else 'N/A'}")
    line(f"End: {session.end_time.strftime('%Y-%m-%d %H:%M') if session.end_time else 'N/A'}")
    line(f"Duration: {str(session.duration) if session.duration else 'N/A'}")
    line(f"Energy Delivered: {session.energy_consumed_kwh if session.energy_consumed_kwh is not None else 'N/A'} kWh")
    line(f"Total: {session.costs if session.costs is not None else '0.00'}")

    p.showPage()
    p.save()
    buffer.seek(0)

    # Build email
    subject = f"Your Volthub charging receipt — Session {session.id}"
    body = (
        f"Hi {full_name},\n\n"
        f"Your charging session #{session.id} at {session.station.name} has completed.\n"
        f"Please find the attached receipt (PDF).\n\n"
        "Thank you for using our service."
    )
    email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [user_email])
    email.attach(f"invoice_session_{session.id}.pdf", buffer.read(), 'application/pdf')

    # Send email (fail_silently=False so you can see errors in worker logs while developing)
    email.send(fail_silently=False)
    buffer.close()

    
    return f"Invoice sent to {user_email} for session {session.id}"