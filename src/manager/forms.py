from django import forms

from src.restaurants.models import Dish
from src.users.models import WaiterModel, UserModel


class UserManagerLoginForm(forms.Form):
    username = forms.CharField(max_length=64)
    password = forms.CharField(max_length=64)
    email = forms.EmailField()
    title = forms.CharField(max_length=32)
    image = forms.ImageField()


# class DishForm(forms.Form):
#     title = forms.CharField(label='Название', max_length=100, required=False)
#     image = forms.ImageField(label='Фото', required=False)  # Поле не обязательно для заполнения
#     price = forms.DecimalField(label='Цена', max_digits=6, decimal_places=2, required=False)
#     categories = forms.CharField(label='Категория', max_length=100, required=False)
#     description = forms.CharField(label='Описание', widget=forms.Textarea, required=False)  # Также не обязательно
#     is_active = forms.BooleanField(label='Активность', required=False, initial=True)

class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['title', 'image', 'price', 'categories', 'description', 'is_active']


class WaiterForm(forms.ModelForm):
    class Meta:
        model = WaiterModel
        fields = ['restaurant', 'user', 'average_rating']


from django.contrib.auth.forms import UserCreationForm


# class ManagerRegistrationForm(UserCreationForm):
#     class Meta:
#         model = UserModel
#         fields = ['username', 'email']

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = UserModel
        fields = ['email', 'password']
