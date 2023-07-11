import os
import uuid
from io import BytesIO

from PIL import Image

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.storage import default_storage

from app import settings


# Constants at the module level, may be moved to constants.py in the future
PROFILE_PICS_UPLOAD_PATH = 'profile_pictures'
POST_IMAGES_UPLOAD_PATH = 'post_images'
PROFILE_PIC_SIZE_TUPLE = (300, 300)


def prepare_image(image, size_tuple=PROFILE_PIC_SIZE_TUPLE):
    """Helper function to resize the image and return a BytesIO object."""
    img = Image.open(image)
    img.thumbnail(size_tuple)
    output = BytesIO()
    img.save(output, format='JPEG', quality=80)
    output.seek(0)
    return output


def save_image_to_location(image, destination):
    """Helper function to save the image to the given location using default_storage."""
    with default_storage.open(destination, 'wb') as destination_file:
        destination_file.write(image.getvalue())


def move_image_to_permanent_location(image, destination):
    """Helper function to move the image to its final destination using default_storage."""
    with default_storage.open(image, 'rb') as temp_file:
        save_image_to_location(temp_file, destination)
    # Delete the temporary file
    default_storage.delete(image)


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
        super().save(*args, **kwargs)

        if self.profile_picture:
            temp_image = prepare_image(self.profile_picture.path)
            permanent_file_path = os.path.join(settings.MEDIA_ROOT, PROFILE_PICS_UPLOAD_PATH, f"{self.id}.jpg")
            save_image_to_location(temp_image, permanent_file_path)
            move_image_to_permanent_location(self.profile_picture.path, permanent_file_path)
            self.profile_picture.name = permanent_file_path

            self.save(update_fields=['profile_picture'])

    class Meta:
        verbose_name_plural = 'Users'


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
        super().save(*args, **kwargs)

        if self.image:
            temp_image = prepare_image(self.image.path)
            permanent_file_path = os.path.join(settings.MEDIA_ROOT, POST_IMAGES_UPLOAD_PATH, f"{self.id}.jpg")
            save_image_to_location(temp_image, permanent_file_path)
            move_image_to_permanent_location(self.image.path, permanent_file_path)
            self.image.name = permanent_file_path

            self.save(update_fields=['image'])


class Tag(models.Model):
    """Tag model for the social media app. 
    Despite deleting user account tags will remain."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                            related_name='tags')
    name = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return self.name
