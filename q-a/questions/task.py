
import time
from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .models import Question,Answer,QLike

@shared_task
def question_created(question_id):
    question = Question.objects.get(id=question_id)
    subject = f'question id {question.id}'
    message = f'dear {question.author} your question created. your question : {question.content}'
    email_host = settings.EMAIL_HOST_USER

    mail_send = send_mail(subject,message,email_host,[question.author.email])


@shared_task
def answer_created(answer_id):
    answer = Answer.objects.get(id=answer_id)
    subject = f'dear {answer.question.author.username}'
    message = f' {answer.author} answered your question : { answer.body }'
    email_host = settings.EMAIL_HOST_USER

    mail_send = send_mail(subject,message,email_host,[answer.question.author.email])

@shared_task
def question_liked(q_id):
    qlike = QLike.objects.get(id=q_id)
    subject = f'Dear {qlike.question.author.username}'
    message = f'user {qlike.liker} liked your question'
    email_host = settings.EMAIL_HOST_USER

    mail_send = send_mail(subject,message,email_host,[qlike.question.author.email])



