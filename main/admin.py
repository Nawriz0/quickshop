from django.contrib import admin
from .models import Product, Category, Order, Banner
from django.utils.html import format_html
from django.db.models import Q
from decimal import Decimal, InvalidOperation

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'image_preview', 'display_description')
    list_filter = ('category', 'price')
    search_fields = ('title', 'description', 'category__name')
    list_per_page = 20
    ordering = ('title',)
    list_editable = ('price',)  # Позволяет редактировать цену прямо в списке
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = 'Изображение'
    
    def display_description(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    display_description.short_description = 'Описание'
    
    def get_search_results(self, request, queryset, search_term):
        # Расширенный поиск по цене
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        try:
            # Поиск по цене (меньше чем, больше чем)
            if '<' in search_term:
                price = Decimal(search_term.replace('<', '').strip())
                queryset |= self.model.objects.filter(price__lt=price)
            elif '>' in search_term:
                price = Decimal(search_term.replace('>', '').strip())
                queryset |= self.model.objects.filter(price__gt=price)
            elif '-' in search_term:
                # Поиск по диапазону цен (например: 100-200)
                price_range = search_term.split('-')
                if len(price_range) == 2:
                    price_min = Decimal(price_range[0].strip())
                    price_max = Decimal(price_range[1].strip())
                    queryset |= self.model.objects.filter(price__range=(price_min, price_max))
        except (ValueError, InvalidOperation):
            pass
            
        return queryset, use_distinct
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'category', 'price')
        }),
        ('Дополнительно', {
            'fields': ('description', 'image'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    list_per_page = 20
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Количество товаров'

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    ordering = ('-created_at',)