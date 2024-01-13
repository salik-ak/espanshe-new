from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email,phone, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,phone = phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email,phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email,phone, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=20,unique=True,verbose_name='phone number',
                             blank=False,help_text='enter 10 digit phone number')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = CustomUserManager()



class UserProfile(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    address_line_1 = models.CharField(blank=True,max_length=100,null=True)
    address_line_2 = models.CharField(blank=True,max_length=100,null=True)
    profile_picture = models.ImageField(blank=True,upload_to='userprofile',null=True)
    state = models.CharField(blank=True,max_length=20,null=True)
    country = models.CharField(blank=True,max_length=20,null=True)
    city = models.CharField(blank=True,max_length=20,null=True)
    wallet = models.FloatField(blank=True,null=True,default=0)


    def __str__(self):
        return self.user.first_name

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
