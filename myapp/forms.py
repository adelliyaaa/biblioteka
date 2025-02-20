from django import forms

from myapp.models.category import Category
from myapp.models.review import Review
from myapp.models.user_profile import UserProfile
from django_select2 import forms as s2forms


from django import forms

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'first_name', 'last_name', 'age', 'favorite_genres', 'read_books']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'favorite_genres': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'read_books': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']



class BookSearchForm(forms.Form):
    title = forms.CharField(label="Название", required=False)
    author = forms.CharField(label="Автор", required=False)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Жанр",
        required=False,
        empty_label="Все жанры"
    )
    start_date = forms.DateField(label="Дата с", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(label="Дата по", required=False, widget=forms.DateInput(attrs={"type": "date"}))
