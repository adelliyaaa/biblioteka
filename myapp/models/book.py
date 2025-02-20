from django.db import models
from django.contrib.auth.models import User

from myapp.models.category import Category


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='media/', null=True, blank=True)
    available = models.BooleanField(default=True)
    publication_date = models.DateField()
    categories = models.ManyToManyField(Category, related_name='books', blank=True)  # Связь с категориями

    def __str__(self):
        return self.title



class BorrowedBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrowed_date = models.DateField(auto_now_add=True)
    return_date = models.DateField()

    def __str__(self):
        return f"{self.book.title} borrowed by {self.user.username}"