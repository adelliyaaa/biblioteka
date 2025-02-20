from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User

from myapp.models.book import Book
from myapp.models.category import Category


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)], blank=True, null=True
    )
    read_books = models.ManyToManyField(Book, related_name='read_by', blank=True)
    favorite_genres = models.ManyToManyField(Category, related_name='fans', blank=True)

    def __str__(self):
        return self.user.username