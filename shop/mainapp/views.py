from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.views.generic import DetailView

from .models import Product, Category, Customer, Cart, CartProduct, Order
from .forms import OrderForm, LoginForm, RegistrationForm
from .utils import recalculate_cart
from .mixins import CartMixin


class BaseView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all().only('title', 'category', 'slug', 'price', 'image')
        context = {
            'products': products,
            'cart': self.cart,
        }
        return render(request, 'mainapp/base.html', context)


class CategoryDetailView(CartMixin, DetailView):
    model = Product
    queryset = Product.objects.all()
    context_object_name = 'latest_products'
    template_name = 'mainapp/base.html'
    slug_url_kwarg = 'slug'


class ProductDetailView(CartMixin, DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        context['categories'] = categories
        context['latest_products'] = Product.objects.all()
        context['cart'] = self.cart
        return context

    context_object_name = 'product'
    template_name = 'mainapp/product_detail.html'
    slug_url_kwarg = 'slug'


class AddToCartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        print(kwargs.get('slug'))
        product = Product.objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, product=product
        )
        if created:
            self.cart.products.add(cart_product)
        else:
            cart_product.qty += 1
            cart_product.save()
        recalculate_cart(self.cart)
        # messages.add_message(request, messages.INFO, 'Товар успешно добавлен в корзину')
        return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, product=product
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalculate_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Товар успешно удален из корзины')
        return HttpResponseRedirect('/cart/')


class ChangeQtyView(CartMixin, View):
    def post(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, product=product
        )
        try:
            cart_product.qty = int(request.POST.get('qty'))
            cart_product.save()
            recalculate_cart(self.cart)
            messages.add_message(request, messages.INFO, 'Количество товара успешно изменено')
        except Exception as ex:
            print(ex)
        return HttpResponseRedirect('/cart/')


class CartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        context = {
            'categories': categories,
            'cart': self.cart,
        }
        return render(request, 'mainapp/cart.html', context)


class CheckoutView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        form = OrderForm(request.POST or None)
        context = {
            'categories': categories,
            'cart': self.cart,
            'form': form,
        }
        return render(request, 'mainapp/checkout.html', context)


class CreateOrderView(CartMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        if form.is_valid():
            customer = Customer.objects.get(user=request.user)
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, 'Спасибо за заказ!')
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/checkout/')


class LoginView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        categories = Category.objects.all()
        context = {'form': form, 'categories': categories, 'cart': self.cart}
        return render(request, 'mainapp/login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'mainapp/login.html', {'form': form})


class RegistrationView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        categories = Category.objects.all()
        context = {'form': form, 'categories': categories, 'cart': self.cart}
        return render(request, 'mainapp/registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address']
            )
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/')
        context = {'form': form, 'cart': self.cart}
        return render(request, 'mainapp/registration.html', context)

class ProfileView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(customer=customer).order_by('-created_at')
        categories = Category.objects.all()
        context = {'customer': customer, 'orders': orders, 'categories': categories, 'cart': self.cart}
        return render(request, 'mainapp/profile.html', context)
