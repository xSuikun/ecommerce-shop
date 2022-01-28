from django.core.mail import send_mail

from shop.celery import app

from .service import send
from .models import Contact


@app.task
def send_spam_email(user_email):
    send(user_email)


@app.task
def send_beat_email():
    contacts = Contact.objects.all().values_list('email', flat=True)
    for contact in contacts:
        send_mail(
            'Вы подписались на рассылку',
            'Мы будем присылать вам много спама каждые 5 минут',
            'tarkovtarkov69@gmail.com',
            [contact],
            fail_silently=False
        )



