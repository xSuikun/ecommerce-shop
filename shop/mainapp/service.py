from django.core.mail import send_mail


def send(email):
    send_mail(
        'Вы подписались на рассылку',
        'Мы будем присылать вам много спама',
        'tarkovtarkov69@gmail.com',
        [email],
        fail_silently=False
    )
