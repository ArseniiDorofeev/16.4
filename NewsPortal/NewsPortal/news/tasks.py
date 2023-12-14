from datetime import timedelta, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django_apscheduler.models import DjangoJob

from .models import Subscriber, News, Post


def send_weekly_newsletter():
    # Определяем даты начала и конца прошлой недели
    today = timezone.now().date()
    last_week_start = today - timedelta(days=today.weekday() + 7)
    last_week_end = today - timedelta(days=today.weekday())

    # Находим новости, добавленные за прошлую неделю
    new_news = News.objects.filter(date_added__gte=last_week_start, date_added__lte=last_week_end)

    if new_news:
        # Получаем список уникальных адресов подписчиков
        subscribers = Subscriber.objects.values_list('email', flat=True).distinct()

        # Собираем текст рассылки
        subject = "Еженедельная рассылка новостей"
        message = "Здравствуйте,\n\n"
        message += "Вот свежие новости, добавленные за прошлую неделю:\n\n"
        for news in new_news:
            message += f"- {news.title}: {news.content[:50]}...\n"
        message += "\nС уважением,\nВаш новостной портал"

        # Отправляем рассылку
        send_mail(subject, message, 'your_email@example.com', subscribers, fail_silently=False)


scheduler = BackgroundScheduler()
scheduler.add_job(send_weekly_newsletter, "cron", day_of_week="fri", hour=12)

DjangoJob.objects.all().delete()  # Очистить предыдущие задания
scheduler.start()


@shared_task
def send_weekly_newsletter():
    last_week = datetime.now() - timedelta(days=7)
    latest_news = Post.objects.filter(pub_date__gte=last_week)

    subject = 'Еженедельная рассылка новостей'
    message = 'Здесь находятся последние новости за прошедшую неделю:\n\n'
    for news in latest_news:
        message += f'- {news.title}\n'
    from_email = 'your@email.com'
    recipient_list = ['subscribed_user@email.com']
    send_mail(subject, message, from_email, recipient_list)
