import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify


def profile_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.bio)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/movies/", filename)


class UserProfile(models.Model):
    owner = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="profile"
    )
    username = models.CharField(max_length=55, unique=True)
    profile_picture = models.ImageField(
        null=True, upload_to=profile_image_file_path
    )
    bio = models.CharField(max_length=255)
    following = models.ManyToManyField(
        to=get_user_model(),
        related_name="user_follows",
        related_query_name="following",
    )
    followers = models.ManyToManyField(
        to=get_user_model(),
        related_name="followers",
        related_query_name="followers",
    )

    class Meta:
        verbose_name_plural = "profile"
        ordering = ["-id"]

    def __str__(self):
        return str(self.username)


class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return str(self.name)


class Post(models.Model):
    author = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=55)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    hashtags = models.ManyToManyField(
        Hashtag, blank=True, related_name="posts"
    )

    class Meta:
        verbose_name_plural = "posts"

    def __str__(self):
        return str(self.text)
