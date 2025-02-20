from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from myapp.forms import UserProfileForm, ReviewForm, BookSearchForm
from myapp.models.book import Book
from myapp.models.category import Category
from myapp.models.review import Review
from myapp.models.user_profile import UserProfile


def get_all_subcategories(category):
    """Рекурсивно находим все подкатегории."""
    subcategories = set(category.subcategories.all())  # предполагаем, что есть related_name='subcategories'
    for subcategory in list(subcategories):
        subcategories.update(get_all_subcategories(subcategory))
    return subcategories

def index(request):
    query = request.GET.get('q')
    books = Book.objects.all()

    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        ).distinct()

    one_year_ago = timezone.now() - timezone.timedelta(days=365)
    new_releases_list = Book.objects.filter(publication_date__gte=one_year_ago).order_by('-publication_date')

    # Пагинация для новинок
    new_releases_paginator = Paginator(new_releases_list, 3)
    new_releases_page = request.GET.get('page') or 1
    new_releases = new_releases_paginator.get_page(new_releases_page)

    recommended_books = Book.objects.none()

    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            favorite_categories = user_profile.favorite_genres.all()

            # Собираем все любимые категории + их подкатегории
            all_favorite_categories = set(favorite_categories)
            for category in favorite_categories:
                all_favorite_categories.update(get_all_subcategories(category))

            recommended_books_list = Book.objects.filter(categories__in=all_favorite_categories).distinct()

            # Пагинация для рекомендаций
            recommended_books_paginator = Paginator(recommended_books_list, 3)
            recommended_books_page = request.GET.get('recommended_page') or 1
            recommended_books = recommended_books_paginator.get_page(recommended_books_page)

        except UserProfile.DoesNotExist:
            pass

    context = {
        'books': books,
        'new_releases': new_releases,
        'recommended_books': recommended_books,
    }
    return render(request, 'myapp/index.html', context)



def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, 'myapp/review_detail.html', {'review': review})


@login_required
def profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)
        user_profile.save()

    user_reviews = Review.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('myapp:profile')
    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        'user_profile': user_profile,
        'form': form,
        'user_reviews': user_reviews,
    }
    return render(request, 'myapp/profile.html', context)

@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('myapp:profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'myapp/edit_profile.html', {'form': form})


def book_list(request):
    books = Book.objects.all()
    paginator = Paginator(books, 12)  # Показывать 12 книг на странице
    page = request.GET.get('page')
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)

    return render(request, 'myapp/book_list.html', {'books': books})


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.all()
    form = ReviewForm()

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user  # если есть авторизация
            review.save()
            return redirect("myapp:book_detail", pk=pk)

    books_by_author = Book.objects.filter(author=book.author).exclude(pk=pk)
    books_by_categories = Book.objects.filter(categories__in=book.categories.all()).exclude(pk=pk)
    recommended_books_list = list({b.pk: b for b in books_by_author | books_by_categories}.values())

    category_include = request.GET.getlist("category_include")
    category_exclude = request.GET.getlist("category_exclude")

    if category_include:
        recommended_books_list = [b for b in recommended_books_list if b.categories.filter(id__in=category_include).exists()]
    if category_exclude:
        recommended_books_list = [b for b in recommended_books_list if not b.categories.filter(id__in=category_exclude).exists()]

    paginator = Paginator(recommended_books_list, 3)
    recommended_page = request.GET.get("recommended_page") or 1
    recommended_books = paginator.get_page(recommended_page)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "myapp/includes/recommended_books.html", {"recommended_books": recommended_books})

    return render(request, "myapp/book_detail.html", {
        "book": book,
        "reviews": reviews,
        "form": form,
        "recommended_books": recommended_books,
        "all_categories": Category.objects.all(),
    })



def review_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'myapp/review_list.html', {'reviews': reviews})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect('/')  # Перенаправление на главную
    else:
        form = UserCreationForm()
    return render(request, 'myapp/register.html', {'form': form})



def BookListByCategoryView(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    # Получаем все подкатегории этой категории
    subcategories = category.subcategories.all()

    # Собираем список всех категорий: текущая + подкатегории
    category_ids = [category.id] + [subcat.id for subcat in subcategories]

    # Фильтруем книги по этим категориям
    books = Book.objects.filter(categories__id__in=category_ids).distinct()

    return render(request, 'myapp/book_list2.html', {'books': books, 'category': category})

def user_profile(request, pk):
    user_profile = get_object_or_404(UserProfile, user__pk=pk)
    user_reviews = Review.objects.filter(user=user_profile.user).order_by('-created_at')

    context = {
        'user_profile': user_profile,
        'user_reviews': user_reviews,
    }
    return render(request, "myapp/user_profile.html", context)



def book_search(request):
    form = BookSearchForm(request.GET)
    books = Book.objects.all()

    if form.is_valid():
        title = form.cleaned_data.get("title")
        author = form.cleaned_data.get("author")
        category = form.cleaned_data.get("category")
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")

        if title:
            books = books.filter(title__icontains=title)
        if author:
            books = books.filter(author__icontains=author)
        if category:
            books = books.filter(categories=category)
        if start_date:
            books = books.filter(publication_date__gte=start_date)
        if end_date:
            books = books.filter(publication_date__lte=end_date)

    return render(request, "myapp/book_search.html", {"form": form, "books": books})
