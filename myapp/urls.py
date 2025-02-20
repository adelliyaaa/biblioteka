from django.urls import path, include

from myapp.views.index import index, book_list, book_detail, review_list, review_detail, profile, register, \
    edit_profile, BookListByCategoryView, user_profile, book_search

app_name = 'myapp'
urlpatterns = [
    path("", index, name="index"),

    path('books/', book_list, name='book_list'),
    path('books/<int:pk>/', book_detail, name='book_detail'),
    path('reviews/', review_list, name='review_list'),
    path('reviews/<int:pk>/', review_detail, name='review_detail'),
    path('profile/', profile, name='profile'),
    path('profile/<int:pk>/', user_profile, name='user_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', register, name='register'),
    path('books/category/<int:category_id>/', BookListByCategoryView, name='books_by_category'),
    path("search/", book_search, name="book_search"),


]