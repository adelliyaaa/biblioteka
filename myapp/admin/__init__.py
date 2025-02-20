from django.contrib import admin

from myapp.models.book import Book, BorrowedBook
from myapp.models.category import Category
from myapp.models.review import Review
from myapp.models.user_profile import UserProfile

admin.site.register(Book)
admin.site.register(UserProfile)
admin.site.register(Review)
admin.site.register(BorrowedBook)
admin.site.register(Category)
