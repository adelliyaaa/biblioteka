from myapp.models.category import Category


def sidebar_categories(request):
    categories = Category.objects.filter(parent=None).prefetch_related('subcategories')
    return {'categories': categories}