from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    """Custom User model for the social media app."""
    email = models.EmailField(unique=True)
    profile_picture = models.URLField(blank=True)
    bio = models.CharField(max_length=255, blank=True)
    is_admin = models.BooleanField(default=False)
    followers = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='following')
    ## posts = models.ManyToManyField('Post', blank=True, related_name='user_posts')
    ## tags = models.ManyToManyField('Tag', blank=True, related_name='user_tags')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
