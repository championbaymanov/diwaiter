from django import forms


class UserManagerLoginForm(forms.Form):
    username = forms.CharField(max_length=64)
    password = forms.CharField(max_length=64)
    email = forms.EmailField()
    title = forms.CharField(max_length=32)
    image = forms.ImageField()


class DishForm(forms.Form):
    title = forms.CharField(label='Название', max_length=100, required=False)
    image = forms.ImageField(label='Фото', required=False)  # Поле не обязательно для заполнения
    price = forms.DecimalField(label='Цена', max_digits=6, decimal_places=2, required=False)
    categories = forms.CharField(label='Категория', max_length=100, required=False)
    description = forms.CharField(label='Описание', widget=forms.Textarea, required=False)  # Также не обязательно
    is_active = forms.BooleanField(label='Активность', required=False, initial=True)
