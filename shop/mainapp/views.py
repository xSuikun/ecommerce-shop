from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.views.generic import DetailView

from .models import Product, Notebook, Smartphone, Category, LatestProducts, Customer, Cart, CartProduct
from .forms import OrderForm
from .utils import recalculate_cart
from .mixins import *


class BaseView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        products = LatestProducts.objects.all(8)
        context = {
            'products': products,
            'cart': self.cart,
        }
        return render(request, 'mainapp/base.html', context)


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'mainapp/base.html'
    slug_url_kwarg = 'slug'


class ProductDetailView(CartMixin, DetailView):
    def dispatch(self, request, *args, **kwargs):
        self.model = eval(kwargs.get('model'))
        queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        context['latest_products'] = LatestProducts.objects.all(4)
        context['cart'] = self.cart
        return context

    context_object_name = 'product'
    template_name = 'mainapp/product_detail.html'
    slug_url_kwarg = 'slug'


class AddToCartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        ct_model = kwargs.get('ct_model')
        product_slug = kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
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
        ct_model = kwargs.get('ct_model')
        product_slug = kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalculate_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Товар успешно удален из корзины')
        return HttpResponseRedirect('/cart/')


class ChangeQtyView(CartMixin, View):
    def post(self, request, *args, **kwargs):
        ct_model = kwargs.get('ct_model')
        product_slug = kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
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
        categories = Category.objects.get_categories_for_header()
        context = {
            'categories': categories,
            'cart': self.cart,
        }
        return render(request, 'mainapp/cart.html', context)


class CheckoutView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_header()
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



