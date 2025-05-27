from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from .models import Product, Order, Category, Banner
from .forms import OrderForm, UserCreationFormCustom
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.conf import settings
import stripe
from django.db.models import Q
import random
from random import choice
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from decimal import Decimal
import json

# Инициализация Stripe API ключом
stripe.api_key = settings.STRIPE_SECRET_KEY

# Главная страница — список товаров
def home(request):
    # Get active banner
    active_banner = Banner.objects.filter(is_active=True).first()
    
    # Get products with cart status
    products = Product.objects.all()
    if 'category' in request.GET:
        products = products.filter(category__slug=request.GET['category'])
    if 'search' in request.GET:
        query = request.GET['search']
        products = products.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    
    # Get product of the day
    try:
        product_of_the_day = choice(list(products))
    except IndexError:
        product_of_the_day = None

    # Add cart and favorite status to products
    products_with_status = []
    for product in products:
        if request.user.is_authenticated:
            is_favorite = product.favorites.filter(id=request.user.id).exists()
        else:
            is_favorite = False
            
        products_with_status.append({
            'product': product,
            'in_cart': str(product.id) in request.session.get('cart', {}),
            'is_favorite': is_favorite
        })

    return render(request, 'main/home.html', {
        'products_with_cart_status': products_with_status,
        'product_of_the_day': product_of_the_day,
        'active_banner': active_banner,
    })

# Страница товара
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = product.favorites.filter(id=request.user.id).exists()
    context = {
        'product': product,
        'title': product.title,
        'is_favorite': is_favorite
    }
    return render(request, 'main/product_detail.html', context)

# Добавить товар в корзину
def add_to_cart(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk)
        cart = request.session.get('cart', {})
        product_id = str(pk)
        
        if product_id in cart:
            messages.info(request, 'Этот товар уже в корзине')
        else:
            cart[product_id] = 1
            request.session['cart'] = cart
            messages.success(request, 'Товар успешно добавлен в корзину')
        
        return redirect('home')
    except Exception as e:
        messages.error(request, 'Произошла ошибка при добавлении товара в корзину')
        return redirect('home')

# Просмотр корзины
def cart_view(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0
    for pk, qty in cart.items():
        product = get_object_or_404(Product, pk=pk)
        product.qty = qty
        product.total = product.price * qty
        total += product.total
        products.append(product)
    return render(request, 'main/cart.html', {'products': products, 'total': total})

# Очистить корзину
def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart')

# Оформление заказа
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Ваша корзина пуста.")
        return redirect('cart')

    # Добавляем отладочную информацию
    print("Debug: STRIPE_PUBLISHABLE_KEY =", settings.STRIPE_PUBLISHABLE_KEY)
    print("Debug: STRIPE_SECRET_KEY exists =", bool(settings.STRIPE_SECRET_KEY))

    total_amount = 0
    order_items_details = []

    for pk, qty in cart.items():
        product = get_object_or_404(Product, pk=pk)
        total_amount += int(product.price * qty * 100)
        order_items_details.append(f"{product.title} (x{qty})")

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            payment_method_id = request.POST.get('payment_method_id')

            try:
                intent = stripe.PaymentIntent.create(
                    amount=total_amount,
                    currency='uzs',
                    payment_method=payment_method_id,
                    confirm=True,
                    description=f"Заказ QuickShop: {', '.join(order_items_details)}"
                )

                if intent.status == 'succeeded':
                    order = form.save(commit=False)
                    order.total = total_amount / 100
                    order.paid = True
                    order.stripe_payment_intent_id = intent.id
                    order.save()
                    request.session['cart'] = {}
                    messages.success(request, 'Ваш заказ успешно оплачен и оформлен!')
                    return redirect('thanks_page')
                elif intent.status == 'requires_action' or intent.status == 'requires_payment_method':
                    messages.error(request, f"Платеж требует дополнительного действия или не удался: {intent.last_payment_error.message if intent.last_payment_error else 'Попробуйте снова'}")
                else:
                    messages.error(request, f"Ошибка платежа: {intent.last_payment_error.message if intent.last_payment_error else 'Неизвестная ошибка'}")

            except stripe.error.StripeError as e:
                messages.error(request, f"Ошибка Stripe: {str(e)}")
            except Exception as e:
                messages.error(request, f"Произошла ошибка: {str(e)}")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = OrderForm()
        try:
            intent = stripe.PaymentIntent.create(
                amount=total_amount,
                currency='uzs',
                payment_method_types=['card'],
            )
            client_secret = intent.client_secret
        except stripe.error.StripeError as e:
            messages.error(request, f"Ошибка при инициализации платежа: {str(e)}")
            client_secret = None
            print("Debug: Stripe Error =", str(e))
        except Exception as e:
            messages.error(request, f"Произошла ошибка: {str(e)}")
            client_secret = None
            print("Debug: General Error =", str(e))

    context = {
        'form': form,
        'total': total_amount / 100,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'client_secret': client_secret if 'client_secret' in locals() else None,
        'debug': settings.DEBUG,  # Добавляем флаг debug в контекст
    }
    print("Debug: Context =", context)
    return render(request, 'main/checkout.html', context)

# Удалить товар из корзины
def remove_from_cart(request, pk):
    try:
        cart = request.session.get('cart', {})
        product_id = str(pk)
        
        if product_id in cart:
            del cart[product_id]
            request.session['cart'] = cart
            messages.success(request, 'Товар успешно удален из корзины')
        
        return redirect('cart')
    except Exception as e:
        messages.error(request, 'Произошла ошибка при удалении товара из корзины')
        return redirect('cart')

# Регистрация пользователя
def register_view(request):
    if request.method == 'POST':
        form = UserCreationFormCustom(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserCreationFormCustom()
    return render(request, 'main/register.html', {'form': form})

# Вход пользователя
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'Добро пожаловать, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

# Выход пользователя
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('home')

# Страница благодарности после успешной оплаты
def thanks_page_view(request):
    return render(request, 'main/thanks.html')

@login_required
def favorites_view(request):
    try:
        user_favorites = request.user.favorite_products.all()
        context = {
            'products': user_favorites,
            'title': 'Избранное'
        }
        return render(request, 'main/favorites.html', context)
    except Exception as e:
        messages.error(request, f'Произошла ошибка: {str(e)}')
        return redirect('home')

@login_required
def toggle_favorite(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    product = get_object_or_404(Product, id=product_id)
    user = request.user
    
    try:
        if product.favorites.filter(id=user.id).exists():
            product.favorites.remove(user)
            status = 'removed'
        else:
            product.favorites.add(user)
            status = 'added'
        return JsonResponse({'status': status})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def create_order(request):
    try:
        if request.method == 'POST':
            cart = request.session.get('cart', {})
            if not cart:
                messages.error(request, 'Ваша корзина пуста')
                return redirect('cart')

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                total_amount=Decimal('0.00')
            )

            total = Decimal('0.00')
            for product_id, quantity in cart.items():
                try:
                    product = Product.objects.get(pk=product_id)
                    total += product.price * Decimal(quantity)
                except Product.DoesNotExist:
                    messages.error(request, f'Товар с ID {product_id} не найден')
                    order.delete()
                    return redirect('cart')

            order.total_amount = total
            order.save()

            request.session['cart'] = {}
            messages.success(request, 'Заказ успешно создан')
            return redirect('home')
    except Exception as e:
        messages.error(request, 'Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте позже.')
        return redirect('cart')

    return redirect('cart') 