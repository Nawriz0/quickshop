from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Order

class UserCreationFormCustom(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # Здесь можно будет добавить поля, если потребуется, например, email
        fields = UserCreationForm.Meta.fields # Оставляем стандартные поля: username, password1, password2

class OrderForm(forms.ModelForm):
    class Meta:
        model =  Order
        fields = ['name', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя Фамилия'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ваш адрес доставки'}),
        }
        labels = {
            'name': 'Имя и Фамилия',
            'address': 'Адрес доставки',
        }