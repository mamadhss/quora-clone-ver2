from django.db import models
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.db.models import signals
from django.dispatch import receiver

class UserAccountManager(BaseUserManager):
    def create_user(self,email,username,password=None,**extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have a username')

        email = self.normalize_email(email)
        user = self.model(email=email,username=username.lower(),**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,username,password):
        user = self.create_user(email,username,password)
        user.is_superuser=True
        user.is_staff = True
        user.save(using=self._db)
        return user  
    

class UserAccount(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(max_length=30,unique=True)
    email =  models.EmailField(max_length=255,unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    objects = UserAccountManager()


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']


    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', blank=True)
    company = models.CharField(max_length=255, blank=True)
    website = models.URLField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    

    def __str__(self):
        return self.user.username

@receiver(signals.post_save,sender=settings.AUTH_USER_MODEL)
def create_profile(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(user=instance)       