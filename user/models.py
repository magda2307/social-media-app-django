from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    """Manager for users in the system."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create, save, and return a new user."""
        if not email:
            raise ValueError("User must have an email address.")
        
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)  # Set encrypted password
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, password):
        """Create, save, and return a new superuser."""
        user = self.create_user(email=email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        
        return user


class User(AbstractBaseUser):
    """Custom User model for the social media app."""
    
    email = models.EmailField(unique=True)
    profile_picture = models.URLField(blank=True)
    bio = models.CharField(max_length=255, blank=True)
    is_admin = models.BooleanField(default=False)
    followers = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='following')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    
    def __str__(self):
        return self.email
    

class Post(models.Model):
    """Post model for the social media app."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    text = models.CharField(max_length=255, blank=False)
    image = models.URLField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    # tags = models.ManyToManyField('Tag', blank=True, related_name='post_tags')
    # likes = models.ManyToManyField(User, blank=True, related_name='liked_posts')
    
    def __str__(self):
        return self.text

class Tag(models.Model):
    """Tag model for the social media app."""
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='tags')
    