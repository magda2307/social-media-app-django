from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

class UserManager(BaseUserManager):
    """Manager for users in the system."""
    def create_user(self, email, password=None, **extra_field):
        """Create, save and return a new user."""
        user = self.model(email=email, **extra_field)
        user.set_password(password) #set encrypted password
        user.save(using = self._db)
    
class User(AbstractBaseUser):
    """Custom User model for the social media app."""
    email = models.EmailField(unique=True)
    profile_picture = models.URLField(blank=True)
    bio = models.CharField(max_length=255, blank=True)
    is_admin = models.BooleanField(default=False)
    followers = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='following')
    ## posts = models.ManyToManyField('Post', blank=True, related_name='user_posts')
    ## tags = models.ManyToManyField('Tag', blank=True, related_name='user_tags')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    
    def __str__(self):
        return self.email
    
