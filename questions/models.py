from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models import signals
from django.utils.text import slugify
import uuid

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_questions'
    )
    slug = models.SlugField(max_length=255,unique=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return f'/{self.category.slug}/{self.slug}/'

class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class QLike(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='q_likes'
    )
    liker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )    

class ALike(models.Model):
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='a_likes'
    )    

    liker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )  

@receiver(signals.pre_save,sender=Category)
def slugify_cat(sender,instance,*args,**kwargs):
    instance.slug = slugify(instance.name)

@receiver(signals.pre_save,sender=Question)
def slugify_content(sender,instance,*args,**kwargs):
    original_slug = slugify(instance.content)
    if Question.objects.filter(slug__iexact=original_slug):
        instance.slug = original_slug+"-"+str(uuid.uuid4())[:4]
    else:
        instance.slug = original_slug    
        




