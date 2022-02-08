from django.contrib import messages
from django.db import models

from mainapp.models import CartProduct, Cart, Product


def _recalculate_cart(cart):
    cart_data = cart.products.aggregate(models.Sum('final_price'), models.Count('id'))
    if cart_data.get('final_price__sum'):
        cart.final_price = cart_data['final_price__sum']
    else:
        cart.final_price = 0
    cart.total_products = cart_data['id__count']
    cart.save()


def _add_product_to_cart(cart: Cart, product: Product, request):
    cart_product, created = CartProduct.objects.get_or_create(
        user=cart.owner, cart=cart, product=product
    )
    if created:
        cart.products.add(cart_product)
    else:
        cart_product.qty += 1
        cart_product.save()
    _recalculate_cart(cart)
    messages.add_message(request, messages.INFO, 'Товар успешно добавлен в корзину')


def _remove_product_from_cart(cart: Cart, product: Product, request):
    cart_product = CartProduct.objects.get(
        user=cart.owner, cart=cart, product=product
    )
    cart.products.remove(cart_product)
    cart_product.delete()
    _recalculate_cart(cart)
    messages.add_message(request, messages.INFO, 'Товар успешно удален из корзины')


def _change_product_qty_in_cart(cart: Cart, product: Product, request):
    cart_product = CartProduct.objects.get(
        user=cart.owner, cart=cart, product=product
    )
    try:
        cart_product.qty = int(request.POST.get('qty'))
        cart_product.save()
        _recalculate_cart(cart)
        messages.add_message(request, messages.INFO, 'Количество товара успешно изменено')
    except Exception as ex:
        print(ex)
