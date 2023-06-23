import os
from io import BytesIO

from PIL import Image

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.storage import default_storage

from app import settings


#Constants at the module level, may be moved to constants.py in future
MAX_TAG_LENGTH = 50
PROFILE_PICS_UPLOAD_PATH = 'profile_pictures'
POST_IMAGES_UPLOAD_PATH = 'post_images'
PROFILE_PIC_SIZE_TUPLE = (300, 300)


def prepare_image_and_save_in_temp(image, size_tuple=PROFILE_PIC_SIZE_TUPLE):
    """Helper function to resize the image that returns the temporary file path."""
    img = Image.open(image)
    img.thumbnail(size_tuple)
    output = BytesIO()
    img.save(output, format='JPEG', quality=80)
    output.seek(0)
    
    temp_file_path = os.path.join(settings.MEDIA_ROOT, 'temp', f"{image.name.split('.')[0]}.jpg")

    with open(temp_file_path,'wb') as temp_file:
        temp_file.write(output.getvalue())
    return temp_file_path

def move_image_to_permanent_location(image, destination):
    """Helper function to move the image to its final destination. (dramatic)"""
    with open(image, 'rb') as temp_file:
        default_storage.save(destination, temp_file) 
    # Delete the temporary file
    os.remove(image)

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
        user.is_staff = True
        user.save(using=self._db)
        
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model for the social media app."""
    
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to=PROFILE_PICS_UPLOAD_PATH, blank=True)
    bio = models.CharField(max_length=255, blank=True)
    is_staff = models.BooleanField(default=False)
    followers = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='following')
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if self.profile_picture:
            temp_file_path = prepare_image_and_save_in_temp(self.profile_picture)
            permanent_file_path = os.path.join(settings.MEDIA_ROOT, PROFILE_PICS_UPLOAD_PATH, f"{self.id}.jpg")
            move_image_to_permanent_location(temp_file_path, permanent_file_path)
            self.profile_picture = permanent_file_path
        super().save(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.save()
        super().save(*args, **kwargs)
        

class Post(models.Model):
    """Post model for the social media app."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    text = models.CharField(max_length=255, blank=False)
    image = models.ImageField(upload_to=POST_IMAGES_UPLOAD_PATH, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')
    likes = models.ManyToManyField(User, blank=True, related_name='liked_posts')

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if self.image:
            temp_file_path = prepare_image_and_save_in_temp(self.image)
            permanent_file_path = os.path.join(settings.MEDIA_ROOT, POST_IMAGES_UPLOAD_PATH, f"{self.id}.jpg")
            move_image_to_permanent_location(temp_file_path, permanent_file_path)
            self.image = permanent_file_path
        super().save(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.save()
        super().save(*args, **kwargs)
        



class Tag(models.Model):
    """Tag model for the social media app. 
    Despite deleting user account tags will remain."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                            related_name='tags')    
    name = models.CharField(max_length=MAX_TAG_LENGTH, blank=False)
    
    def __str__(self):
        return self.name