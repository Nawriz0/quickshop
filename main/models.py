from django.db import models
from django.templatetags.static import static
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    # Можно добавить изображение для категории, если нужно
    # image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    favorites = models.ManyToManyField(User, related_name='favorite_products', blank=True)

    def __str__(self):
        return self.title

    @property
    def in_favorites(self):
        if hasattr(self, '_in_favorites'):
            return self._in_favorites
        return False

class Order(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(max_length=200, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Заказ №{self.id} на {self.total} {'(Оплачен)' if self.paid else '(Не оплачен)'}"

class Banner(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    description = models.TextField('Описание', max_length=500)
    image = models.ImageField('Изображение', upload_to='banners/')
    button_text = models.CharField('Текст кнопки', max_length=50, default='Подробнее')
    button_link = models.CharField('Ссылка кнопки', max_length=200)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'
        ordering = ('-created_at',)

    def __str__(self):
        return self.title
