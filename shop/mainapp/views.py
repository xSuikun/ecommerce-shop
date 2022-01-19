from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.db.models import Count, Case, When, Avg
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import Product, Category, Customer, Cart, CartProduct, Order, UserProductRelation
from .forms import OrderForm, LoginForm, RegistrationForm
from .permissions import IsOwnerOrStaffOrReadOnly
from .utils import recalculate_cart
from .mixins import CartMixin
from .serializers import ProductSerializer, CategorySerializer, UserProductRelationSerializer


class BaseView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all().only('title', 'price', 'discount', 'image', 'slug')
        context = {
            'products': products,
            'cart': self.cart,
        }
        return render(request, 'mainapp/base.html', context)


class CategoryDetailView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        category_name = kwargs.get('slug')
        products = Product.objects.filter(category__slug=category_name)
        context = {'products': products}
        return render(request, 'mainapp/category_detail.html', context)


class ProductDetailView(CartMixin, DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specifications'] = self.get_object().get_features()
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
        context = {
            'cart': self.cart,
        }
        return render(request, 'mainapp/cart.html', context)


class CheckoutView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        context = {
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


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all().annotate(
            likes=Count(Case(When(userproductrelation__like=True, then=1)))
        ).select_related('category').prefetch_related('viewers').order_by('id')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filter_fields = ['title', 'slug']
    search_fields = ['title', 'slug']
    ordering_fields = ['title', 'slug']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filter_fields = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'slug']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserProductRelationView(UpdateModelMixin, GenericViewSet):
    queryset = UserProductRelation.objects.all()
    serializer_class = UserProductRelationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'product'

    def get_object(self):
        obj, created = UserProductRelation.objects.get_or_create(user=self.request.user, product_id=self.kwargs['product'])
        return obj

